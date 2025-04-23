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

    def fetch(self) -> pd.DataFrame:
        """
        Fetch real-time Bitcoin snapshot from CoinGecko.

        :return: A one-row DataFrame containing current Bitcoin data.
        """
        df = fetch_full_bitcoin_snapshot()
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

    def run(self) -> dict:
        """
        Execute the full workflow: fetch, append, validate, and summarize.

        :return: Dictionary of validation results.
        """
        print("[START] Fetching Bitcoin price data...")
        df = self.fetch()
        self.append_to_log(df)

        full_df = pd.read_csv(self.log_file)

        float_cols = [
            "price_usd", "market_cap", "total_volume", "market_cap_rank",
            "circulating_supply", "developer_score", "community_score", "ath", "atl"
        ]
        full_df[float_cols] = full_df[float_cols].astype(float)

        check_time_interval(full_df)

        result = self.validate(full_df)

        print("[VALIDATION SUMMARY]")
        print(f"Success: {result['success']}")
        print(f"Passed: {result['statistics']['successful_expectations']} / {result['statistics']['evaluated_expectations']}")

        summarize_validation_result(result)

        context = gx.get_context()
        context.build_data_docs()
        print("Report available at: file:///workspace/gx/uncommitted/data_docs/local_site/index.html")

        print("[DONE] Script complete.")
        return result
