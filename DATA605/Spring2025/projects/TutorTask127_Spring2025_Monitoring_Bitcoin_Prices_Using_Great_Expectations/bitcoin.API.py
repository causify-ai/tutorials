"""
bitcoin.API.py

Provides the BitcoinAPI class for real-time ingestion, validation, and documentation
of Bitcoin price data using Great Expectations. Includes functionality to fetch
Bitcoin data from CoinGecko, append to logs, validate data quality,
and generate data documentation automatically.
"""

import pandas as pd
import great_expectations as gx
from bitcoin_utils import (
    fetch_full_bitcoin_snapshot,
    save_to_csv,
    validate_data,
    summarize_validation_result,
    check_time_interval
)


class BitcoinAPI:
    """
    Class that provides methods to fetch, log, and validate Bitcoin data.
    """

    def __init__(self, log_file: str = "bitcoin_price_log.csv"):
        """
        Initialize the API with a target CSV log file.

        :param log_file: Path to the CSV file for storing data.
        """
        self.log_file = log_file

    def fetch(self, verbose: bool = True) -> pd.DataFrame:
        """
        Fetch real-time Bitcoin snapshot from CoinGecko.

        :param verbose: Whether to print the fetched DataFrame.
        :return: A one-row DataFrame containing current Bitcoin data.
        """
        df = fetch_full_bitcoin_snapshot()
        if verbose:
            print(df)
        return df

    def append_to_log(self, df: pd.DataFrame) -> None:
        """
        Append a new row of data to the CSV log file.

        :param df: DataFrame to be appended.
        """
        save_to_csv(df, self.log_file)

    def validate(self, df: pd.DataFrame) -> dict:
        """
        Validate the data using Great Expectations.

        :param df: The DataFrame to validate.
        :return: Dictionary of validation results.
        """
        return validate_data(df)

    def run(self, verbose: bool = True) -> dict:
        """
        Execute the full workflow: fetch, append, validate, and summarize.

        :param verbose: If True, display detailed logs and validation summary.
        :return: Dictionary of validation results, or {'success': False, 'skipped': True} if fetch failed or incomplete.
        """
        if verbose:
            print("[START] Fetching Bitcoin price data...")

        df = self.fetch(verbose=verbose)

        # Check for empty or None
        if df is None or df.empty:
            print("[WARNING] Fetch failed or returned empty DataFrame. Skipping this iteration.")
            return {"success": False, "skipped": True}

        # Skip if all critical columns are NaN (excluding timestamp and valid)
        critical_cols = [col for col in df.columns if col not in ("timestamp", "valid")]
        if df[critical_cols].isnull().all(axis=1).any():
            print("[WARNING] Fetched row has all critical fields null. Skipping this iteration.")
            return {"success": False, "skipped": True}

        self.append_to_log(df)

        # Load full dataset for validation
        full_df = pd.read_csv(self.log_file)

        float_cols = [
            "price_usd", "market_cap", "total_volume", "market_cap_rank",
            "circulating_supply", "developer_score", "community_score", "ath", "atl"
        ]
        full_df[float_cols] = full_df[float_cols].astype(float)

        check_time_interval(full_df)

        result = self.validate(full_df)

        if verbose:
            print("[VALIDATION SUMMARY]")
            print(f"Success: {result['success']}")
            print(f"Passed: {result['statistics']['successful_expectations']} / {result['statistics']['evaluated_expectations']}")
            summarize_validation_result(result)

            context = gx.get_context()
            context.build_data_docs()
            print("Report available at: file:///workspace/gx/uncommitted/data_docs/local_site/index.html")

            print("[DONE] Script complete.")

        return result
