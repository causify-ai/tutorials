#!/usr/bin/env python
"""
Convert the dataset-per-row metadata of the Gridstatus metadata into a series-
per-row schema and upload the result back into the same S3 bucket.

> python causal_automl/postprocess_gridstatus_metadata.py \
    --aws_profile ck \
    --bucket_path s3://causify-data-collaborators/causal_automl/metadata/ \
    --input_version v1.0 \
    --output_version v2.0

Import as:

import causal_automl.postprocess_gridstatus_metadata as capogrme
"""

import argparse
import ast
import io
import logging
import os
import re
from typing import Any, Dict, List

import helpers.hdbg as hdbg
import helpers.hio as hio
import helpers.hs3 as hs3
import pandas as pd

# Configure logger.
hdbg.init_logger(verbosity=logging.INFO)
_LOG = logging.getLogger(__name__)


# #############################################################################
# _GridstatusMetadataWriter
# #############################################################################


class _GridstatusMetadataWriter:
    """
    Save Gridstatus metadata and upload to S3.
    """

    def __init__(
        self,
        bucket_path: str,
        aws_profile: str,
        cache_dir: str = "tmp.download_metadata_cache/",
    ) -> None:
        """
        Initialize the writer for saving postprocessed metadata to S3.

        :param bucket_path: base S3 path where files will be uploaded
            (e.g., "s3://bucket/dir/")
        :param aws_profile: AWS CLI profile name used for authentication
        :param cache_dir: cache directory path
        """
        self._bucket_path = bucket_path
        self._aws_profile = aws_profile
        self.cache_dir = cache_dir

    def write_df_to_s3(self, df: pd.DataFrame, file_name: str) -> None:
        """
        Save the data as a local CSV file and upload it to S3.

        :param df: data to be saved to S3
        :param file_name: local file name for saving
        """
        local_file_path = os.path.join(self.cache_dir, file_name)
        hio.create_dir(os.path.dirname(local_file_path), incremental=True)
        # Save CSV locally.
        df.to_csv(local_file_path, index=False)
        _LOG.debug("Saved CSV locally to: %s", local_file_path)
        # Upload CSV to the specified S3 bucket.
        bucket_file_path = self._bucket_path + file_name
        hs3.copy_file_to_s3(local_file_path, bucket_file_path, self._aws_profile)
        _LOG.debug("Uploaded to S3: %s", bucket_file_path)


def _load_data(file_path: str, aws_profile: str) -> pd.DataFrame:
    """
    Load data from S3 path to a dataframe.

    :param file_path: S3 path of the data to load from
    :param aws_profile: aws profile that accesses S3 bucket
    :return: the queried metadata
    """
    file = hs3.from_file(file_path, aws_profile=aws_profile)
    df = pd.read_csv(io.StringIO(file))
    _LOG.info("Data Successfully Downloaded.")
    return df


def _prettify(col: str) -> str:
    """
    Convert snake_case to Title Case.

    E.g., “spinning_reserves” to “Spinning Reserves”

    :param col: column name to prettify
    :return: prettified column name
    """
    tokens = re.sub(r"[_\s]+", " ", col).strip().split()
    prettified = " ".join(t.capitalize() for t in tokens)
    return prettified


def _build_series_row(
    base_row: pd.Series,
    col_name: str,
    dataset_id: str,
    dataset_name: str,
) -> Dict[str, Any]:
    """
    Build new rows with the `id_series` and `name_series` columns.

    :param base_row: original row
    :param col_name: column name to prettify
    :param dataset_id: id of the data series
    :param dataset_name: name of the collection of series
    :return: modified row
    """
    # Start with the original row.
    new_row: Dict[str, object] = base_row.to_dict()
    # Add the two series identifiers.
    new_row["id_series"] = f"{dataset_id}.{col_name}"
    new_row["name_series"] = f"{dataset_name} / {_prettify(col_name)}"
    return new_row


def _explode_dataset_row(row: pd.Series) -> List[Dict[str, Any]]:
    """
    Transform a single row into the row-per-series view.

    E.g.,
    Input row:
    id                                      name                    ....
    caiso_as_prices                         CAISO AS Prices         ....

    Output row:
    id                                      name                    ....
    caiso_as_prices                         CAISO AS Prices         ....
    caiso_as_prices                         CAISO AS Prices         ....
    caiso_as_prices                         CAISO AS Prices         ....
    caiso_as_prices                         CAISO AS Prices         ....
    caiso_as_prices                         CAISO AS Prices         ....
    caiso_as_prices                         CAISO AS Prices         ....
    /
    id_series                               name_series
    caiso_as_prices.non_spinning_reserves   CAISO AS Prices / Non Spinning Reserves
    caiso_as_prices.regulation_down         CAISO AS Prices / Regulation Down
    caiso_as_prices.regulation_mileage_down CAISO AS Prices / Regulation Mileage Down
    caiso_as_prices.regulation_mileage_up   CAISO AS Prices / Regulation Mileage Up
    caiso_as_prices.regulation_up           CAISO AS Prices / Regulation Up
    caiso_as_prices.spinning_reserves       CAISO AS Prices / Spinning Reserves


    :param row: row to transform
    :return: the exploded row
    """
    dataset_id: str = row["id"]
    dataset_name: str = row["name"]
    # Ignore primary key columns.
    ignore_cols = set(ast.literal_eval(row["primary_key_columns"]))
    # Iterate through all columns and generate the row-per-series view.
    exploded: List[Dict[str, Any]] = []
    for col_meta in ast.literal_eval(row["all_columns"]):
        col_name: str = col_meta["name"]
        if col_meta.get("is_datetime") or col_name in ignore_cols:
            continue
        exploded.append(
            _build_series_row(row, col_name, dataset_id, dataset_name)
        )
    return exploded


def create_series_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform the whole dataset into the row-per-series view.

    E.g.,
    Input dataset:
    id                                      name                    ....
    caiso_as_prices                         CAISO AS Prices         ....
    ...

    Output dataset:
    id_series                               name_series
    caiso_as_prices.non_spinning_reserves   CAISO AS Prices / Non Spinning Reserves
    caiso_as_prices.regulation_down         CAISO AS Prices / Regulation Down
    caiso_as_prices.regulation_mileage_down CAISO AS Prices / Regulation Mileage Down
    caiso_as_prices.regulation_mileage_up   CAISO AS Prices / Regulation Mileage Up
    caiso_as_prices.regulation_up           CAISO AS Prices / Regulation Up
    caiso_as_prices.spinning_reserves       CAISO AS Prices / Spinning Reserves
    ...
    /
    id                                      name                    ....
    caiso_as_prices                         CAISO AS Prices         ....
    caiso_as_prices                         CAISO AS Prices         ....
    caiso_as_prices                         CAISO AS Prices         ....
    caiso_as_prices                         CAISO AS Prices         ....
    caiso_as_prices                         CAISO AS Prices         ....
    caiso_as_prices                         CAISO AS Prices         ....
    ...

    :param df: data to transform
    :return: transformed data
    """
    exploded_rows: List[Dict[str, Any]] = []
    for _, dataset_row in df.iterrows():
        exploded_rows.extend(_explode_dataset_row(dataset_row))
    result = pd.DataFrame(exploded_rows)
    # Arrange according to desired ordering.
    leading = ["id_series", "name_series"]
    remaining = [c for c in result.columns if c not in leading]
    transformed_df = result[leading + remaining]
    return transformed_df


def _parse() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--aws_profile", default="ck", help="AWS CLI profile for authentication"
    )
    parser.add_argument(
        "--bucket_path",
        default="s3://causify-data-collaborators/causal_automl/metadata/",
        help="Destination S3 directory (trailing slash optional)",
    )
    parser.add_argument(
        "--input_version",
        default="v1.0",
        help="Version of the source metadata file",
    )
    parser.add_argument(
        "--output_version", default="v2.0", help="Version tag for the result file"
    )
    return parser.parse_args()


def _main(args: argparse.Namespace) -> None:
    # Load data.
    src_file = (
        f"{args.bucket_path.rstrip('/')}/gridstatus_metadata_original_"
        f"{args.input_version}.csv"
    )
    gs_meta = _load_data(src_file, args.aws_profile)
    # Transform data to a row-per-series view.
    gs_meta_rps = create_series_metadata(gs_meta)
    # Save transformed dataset to S3.
    writer = _GridstatusMetadataWriter(args.bucket_path, args.aws_profile)
    dst_file = f"gridstatus_metadata_original_{args.output_version}.csv"
    writer.write_df_to_s3(gs_meta_rps, dst_file)


if __name__ == "__main__":
    _main(_parse())
