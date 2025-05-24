#!/usr/bin/env python3
"""
Download metadata from the EIA v2 API and upload it to S3.

Usage:
> python download_eia_metadata.py --category <CATEGORY> --api_key <API_KEY> --version_num <VERSION_NUM>

This script traverses the EIA v2 API under a specified category, collects all time series
metadata, and writes the metadata and associated parameter values to an S3 bucket in versioned
CSV files.

Outputs:
    - A flattened metadata index (one row per frequency and metric combination).
    - A parameter (facet value) CSV per dataset.

Arguments:
    --category       Root category path under the EIA v2 API.
    --api_key        EIA API key used to authenticate requests.
    --version_num    Metadata version used in filenames and output paths (e.g., '1.0').
"""

import argparse
import logging
import os

import helpers.hdbg as hdbg
import helpers.hio as hio
import helpers.hs3 as hs3
import helpers.hparser as hparser
import pandas as pd

import causal_automl.TutorTask401_EIA_metadata_downloader_pipeline.eia_utils as catemdpeu

_LOG = logging.getLogger(__name__)


# #############################################################################
# _EiaMetadataWriter
# #############################################################################


class _EiaMetadataWriter:
    """
    Save EIA metadata and upload to S3.
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


# #############################################################################
# CLI entry point
# #############################################################################


def _extract_and_upload_metadata(
    category: str,
    api_key: str,
    version_num: str,
    bucket_path: str,
    aws_profile: str,
) -> None:
    """
    Extract metadata from the EIA API and upload both metadata and facet values
    to S3.

    :param category: root API category (e.g., "electricity")
    :param api_key: EIA API key
    :param version_num: version tag (e.g., "1.0")
    :param bucket_path: target S3 bucket path
    :param aws_profile: AWS profile name
    """
    # Extract metadata.
    downloader = catemdpeu.EiaMetadataDownloader(category, api_key, version_num)
    df_metadata, param_entries = downloader.run_metadata_extraction()
    # Write to S3 bucket.
    writer = _EiaMetadataWriter(bucket_path, aws_profile)
    for df_facet, facet_file_path in param_entries:
        writer.write_df_to_s3(df_facet, facet_file_path)
    metadata_file_path = f"eia_{category}_metadata_original_v{version_num}.csv"
    writer.write_df_to_s3(df_metadata, metadata_file_path)


def _parse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--category",
        required=True,
        help="Root category path (e.g. electricity, petroleum)",
    )
    parser.add_argument("--api_key", required=True, help="EIA API Key")
    parser.add_argument(
        "--version_num",
        required=True,
        help="Metadata version (e.g. '1.0') used in filenames and S3 paths",
    )
    parser.add_argument(
        "--bucket_path",
        default="s3://causify-data-collaborators/causal_automl/metadata/",
        help="S3 bucket to upload",
    )
    parser.add_argument("--aws_profile", default="ck", help="AWS profile to use")
    hparser.add_verbosity_arg(parser)
    return parser


def _main(parser: argparse.ArgumentParser) -> None:
    args = parser.parse_args()
    hdbg.init_logger(verbosity=args.log_level, use_exec_path=True)
    _extract_and_upload_metadata(
        args.category,
        args.api_key,
        args.version_num,
        args.bucket_path,
        args.aws_profile,
    )


if __name__ == "__main__":
    _main(_parse())
