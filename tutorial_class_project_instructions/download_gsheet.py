"""
Script to fetch the Google sheet, download it and store it for future use.
This removes the dependency of fetching the file multiple times and enables faster
re-use of the downloaded version.

> python download_gsheet.py \
    --sheet_url " " \
    --tab_name " " \
    --output_csv_path " " \
    --secret_path "./secrets/my_service_account.json"
"""
import argparse
import pandas as pd
import logging
import helpers_root.helpers.hgoogle_drive_api as hgodrapi


_LOG = logging.getLogger(__name__)

def extract_sheet(sheet_url, tab_name, csv_path, service_key_path):
    credentials = hgodrapi.get_credentials(service_key_path=service_key_path)
    _LOG.info("Reading Google Sheet %s: ", sheet_url)
    _LOG.info("Using credentials from: %s", service_key_path)
    df = hgodrapi.read_google_file(sheet_url, tab_name=tab_name, credentials=credentials)

    df.to_csv(csv_path, index=False)
    print(f"Sheet downloaded and saved to {csv_path}")

def main():
    parser = argparse.ArgumentParser(description="Download Google Sheet tab and save as CSV")
    parser.add_argument("--sheet_url", required=True, help="URL of the Google Sheet")
    parser.add_argument("--tab_name", required=True, help="Tab name (default: first tab)")
    parser.add_argument("--output_csv_path", required=True, help="Output CSV file path")
    parser.add_argument("--secret_path", required=False, help="Path to service account key (optional)")

    args = parser.parse_args()
    extract_sheet(args.sheet_url, args.tab_name, args.output_csv_path, args.secret_path)

    


if __name__ == "__main__":
    main()
