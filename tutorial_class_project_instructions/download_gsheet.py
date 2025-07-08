"""
Script to fetch the Google sheet, download it and store it for future use. This
removes the dependency of fetching the file multiple times and enables faster
re-use of the downloaded version.

> python download_gsheet.py \
    --sheet_url " " \
    --tab_name " " \
    --output_csv_path " " \
    --secret_path " "

Import as:

import tutorial_class_project_instructions.download_gsheet as tcpidogs
"""

import argparse
import logging

import helpers_root.helpers.hgoogle_drive_api as hgodrapi
import helpers_root.helpers.hparser as hparser

_LOG = logging.getLogger(__name__)


def _extract_sheet(
    sheet_url: str, tab_name: str, csv_path: str, service_key_path: str
) -> None:
    credentials = hgodrapi.get_credentials(service_key_path=service_key_path)
    _LOG.info("Reading Google Sheet %s: ", sheet_url)
    _LOG.info("Using credentials from: %s", service_key_path)
    df = hgodrapi.read_google_file(
        sheet_url, tab_name=tab_name, credentials=credentials
    )
    df.to_csv(csv_path, index=False)
    print(f"Sheet downloaded and saved to {csv_path}")


def _parse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--sheet_url", required=True, help="URL of the Google Sheet"
    )
    parser.add_argument(
        "--tab_name", required=True, help="Tab name (default: first tab)"
    )
    parser.add_argument(
        "--output_csv_path", required=True, help="Output CSV file path"
    )
    parser.add_argument(
        "--secret_path",
        required=False,
        help="Path to service account key (optional)",
    )
    hparser.add_verbosity_arg(parser)
    return parser


def _main(parser: argparse.ArgumentParser) -> None:
    args = parser.parse_args()
    _extract_sheet(
        args.sheet_url, args.tab_name, args.output_csv_path, args.secret_path
    )


if __name__ == "__main__":
    _main(_parse())
