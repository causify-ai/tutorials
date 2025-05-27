"""
Import as:

import causal_automl.postprocess_gridstatus_metadata as capogrme
"""

import ast
import io
import logging
import os
import re
from typing import Dict, Iterable, List

import helpers.hdbg as hdbg
import helpers.henv as henv
import helpers.hio as hio
import helpers.hpandas as hpandas
import helpers.hs3 as hs3
import pandas as pd

# Configure logger.
hdbg.init_logger(verbosity=logging.INFO)
_LOG = logging.getLogger(__name__)

# Print system signature.
_LOG.info("%s", henv.get_system_signature()[0])


# #############################################################################
# _GridstatusMetadataWriter
# #############################################################################


class _GridstatusMetadataWriter:
    """
    Save Gridstatus metadata and upload to S3.
    """

    def __init__(self, bucket_path: str, aws_profile: str) -> None:
        """
        Initialize the writer for saving metadata and facet values to S3.

        :param bucket_path: base S3 path where files will be uploaded
            (e.g., "s3://bucket/dir/")
        :param aws_profile: AWS CLI profile name used for authentication
        """
        self._bucket_path = bucket_path
        self._aws_profile = aws_profile

    def write_df_to_s3(self, df: pd.DataFrame, file_name: str) -> None:
        """
        Save the data as a local CSV file and upload it to S3.

        :param df: data to be saved to S3
        :param file_name: local file name for saving
        """
        cache_dir = "tmp.download_metadata_cache/"
        local_file_path = os.path.join(cache_dir, file_name)
        hio.create_dir(os.path.dirname(local_file_path), incremental=True)
        # Save CSV locally.
        df.to_csv(local_file_path, index=False)
        _LOG.debug("Saved CSV locally to: %s", local_file_path)
        # Upload CSV to the specified S3 bucket.
        bucket_file_path = self._bucket_path + file_name
        hs3.copy_file_to_s3(local_file_path, bucket_file_path, self._aws_profile)
        _LOG.debug("Uploaded to S3: %s", bucket_file_path)


def _load_data(file_path: str) -> pd.DataFrame:
    """
    Load data from file path to a dataframe.

    :param file_path: path of the data to load from
    :return: dataframe of the loaded data
    """
    file = hs3.from_file(file_path, aws_profile="ck")
    df = pd.read_csv(io.StringIO(file))
    _LOG.info("shape: %s", df.shape)
    _LOG.info("columns: %s", df.columns)
    _LOG.info("df: \n %s", hpandas.df_to_str(df, log_level=logging.INFO))
    return df


def _prettify(col: str) -> str:
    """
    Convert snake_case to Title Case.

    E.g., “spinning_reserves” to “Spinning Reserves”

    :param col: column name to prettify
    :return: prettified column name
    """
    tokens = re.sub(r"[_\s]+", " ", col).strip().split()
    return " ".join(t.capitalize() for t in tokens)


def _build_series_row(
    base_row: pd.Series,
    col_name: str,
    dataset_id: str,
    dataset_name: str,
) -> Dict[str, object]:
    """
    Build new rows with the `id_series` and `num_series` columns.

    :param base_row: original row
    :param col_name: column name to prettify
    """
    nice_col_name = _prettify(col_name)
    # Start with the original row.
    new_row: Dict[str, object] = base_row.to_dict()
    # Add the two series identifiers.
    new_row["id_series"] = f"{dataset_id}.{col_name}"
    new_row["name_series"] = f"{dataset_name} / {nice_col_name}"
    return new_row


def _explode_dataset_row(row: pd.Series) -> Iterable[Dict[str, object]]:
    """
    Transform a single row into the row-per-series view.

    :param row: row to transform
    :return: the exploded row
    """
    dataset_id: str = row["id"]
    dataset_name: str = row["name"]
    # Ignore primary key columns.
    ignore_cols = set(ast.literal_eval(row["primary_key_columns"]))
    # Iterate through all columns and generate the row-per-series view.
    for col_meta in ast.literal_eval(row["all_columns"]):
        col_name: str = col_meta["name"]
        if col_meta.get("is_datetime") or col_name in ignore_cols:
            continue
        yield _build_series_row(row, col_name, dataset_id, dataset_name)


def create_series_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform the whole dataset into the row-per-series view.

    :param df: data to transform
    :return: transformed data
    """
    exploded_rows: List[Dict[str, object]] = [
        row
        for _, dataset_row in df.iterrows()
        for row in _explode_dataset_row(dataset_row)
    ]
    result = pd.DataFrame(exploded_rows)
    # Arrange according to desired ordering.
    leading = ["id_series", "name_series"]
    remaining = [c for c in result.columns if c not in leading]
    return result[leading + remaining]


# Main flow.
if __name__ == "__main__":
    # Configure S3.
    aws_profile = "ck"
    bucket_root = hs3.get_s3_bucket_path(aws_profile)
    bucket_path = "s3://causify-data-collaborators/causal_automl/metadata/"
    file_name = "gridstatus_metadata_original_v2.0.csv"
    writer = _GridstatusMetadataWriter(bucket_path, aws_profile)
    # Load data.
    v1_path = (
        "s3://causify-data-collaborators/causal_automl/metadata/"
        "gridstatus_metadata_original_v1.0.csv"
    )
    gs_meta = _load_data(v1_path)
    # Transform data to a row-per-series view.
    gs_meta_rps = create_series_metadata(gs_meta)
    # Save transformed dataset to S3.
    writer.write_df_to_s3(gs_meta_rps, file_name)
