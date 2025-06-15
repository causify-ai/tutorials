import httpx
import pandas as pd
from datetime import datetime
import os
import great_expectations as gx

def fetch_full_bitcoin_snapshot() -> pd.DataFrame:
    """
    Fetch a comprehensive snapshot of Bitcoin data from the CoinGecko API.

    :return: Single-row DataFrame containing the latest Bitcoin metadata.
    """
    url = "https://api.coingecko.com/api/v3/coins/bitcoin"
    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        market_data = data.get("market_data", {})

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "last_updated": data.get("last_updated"),
            "price_usd": market_data.get("current_price", {}).get("usd"),
            "price_24h_change": market_data.get("price_change_percentage_24h"),
            "market_cap": market_data.get("market_cap", {}).get("usd"),
            "market_cap_rank": data.get("market_cap_rank"),
            "total_volume": market_data.get("total_volume", {}).get("usd"),
            "circulating_supply": market_data.get("circulating_supply"),
            "developer_score": data.get("developer_score"),
            "community_score": data.get("community_score"),
            "ath": market_data.get("ath", {}).get("usd"),
            "atl": market_data.get("atl", {}).get("usd"),
            "valid": True
        }

        return pd.DataFrame([result])

    except Exception as e:
        print(f"[ERROR] Failed to fetch full Bitcoin data: {e}")
        return pd.DataFrame([{  # fallback in case of failure
            "timestamp": datetime.utcnow().isoformat(),
            "last_updated": None,
            "price_usd": None,
            "price_24h_change": None,
            "market_cap": None,
            "market_cap_rank": None,
            "total_volume": None,
            "circulating_supply": None,
            "developer_score": None,
            "community_score": None,
            "ath": None,
            "atl": None,
            "valid": False
        }])

def save_to_csv(df: pd.DataFrame, filename: str = "bitcoin_price_log.csv") -> None:
    """
    Append the given DataFrame to a CSV file.

    :param df: DataFrame to be appended.
    :param filename: Path to the target CSV file.
    """
    file_exists = os.path.isfile(filename)
    df.to_csv(filename, mode='a', header=not file_exists, index=False)
    print(f"[INFO] Data saved to {filename} ({'new file' if not file_exists else 'appended'})")

def fetch_and_log_price(output_file: str = "bitcoin_price_log.csv") -> None:
    """
    Fetch the current Bitcoin snapshot and save it to a CSV file.

    :param output_file: CSV file to write the data into.
    """
    df = fetch_full_bitcoin_snapshot()
    print(df)
    save_to_csv(df, output_file)

def check_time_interval(df: pd.DataFrame, threshold_minutes: int = 60) -> bool:
    """
    Check whether the last two data entries are within the defined interval.

    :param df: DataFrame containing a 'timestamp' column.
    :param threshold_minutes: Maximum allowed time difference in minutes.
    :return: True if the interval is acceptable, False otherwise.
    """
    if len(df) < 2:
        print("[INFO] Not enough data points to check time interval.")
        return True

    try:
        df_sorted = df.sort_values(by="timestamp")
        t1 = pd.to_datetime(df_sorted.iloc[-2]["timestamp"])
        t2 = pd.to_datetime(df_sorted.iloc[-1]["timestamp"])
        delta_minutes = abs((t2 - t1).total_seconds()) / 60

        print(f"[INFO] Time difference between last 2 entries: {delta_minutes:.2f} minutes")
        return delta_minutes <= threshold_minutes
    except Exception as e:
        print(f"[ERROR] Failed to calculate time interval: {e}")
        return False

def validate_data(df: pd.DataFrame, suite_name: str = "bitcoin_suite", datasource_name: str = "my_datasource") -> dict:
    """
    Validate the input DataFrame using Great Expectations.

    :param df: DataFrame to validate.
    :param suite_name: Name of the expectation suite to use.
    :param datasource_name: Name of the GE datasource configuration.
    :return: Dictionary containing validation results.
    """
    context = gx.get_context()

    batch_request = gx.core.batch.RuntimeBatchRequest(
        datasource_name=datasource_name,
        data_connector_name="default_runtime_data_connector_name",
        data_asset_name="my_runtime_asset_name",
        runtime_parameters={"batch_data": df},
        batch_identifiers={"runtime_batch_identifier_name": "some_id"}
    )

    validator = context.get_validator(
        batch_request=batch_request,
        expectation_suite_name=suite_name
    )

    # Expectations
    validator.expect_column_values_to_be_between("price_usd", min_value=20000, max_value=100000)
    validator.expect_column_values_to_not_be_null("price_usd")
    validator.expect_column_values_to_not_be_null("timestamp")
    validator.expect_column_values_to_not_be_null("last_updated")
    validator.expect_column_values_to_be_of_type("market_cap", "float")
    validator.expect_column_values_to_be_between("market_cap", min_value=3e11, max_value=2.5e12)
    validator.expect_column_values_to_be_of_type("total_volume", "float")
    validator.expect_column_values_to_be_between("total_volume", min_value=5e9, max_value=1e11)
    validator.expect_column_values_to_be_between("market_cap_rank", min_value=1, max_value=300)
    validator.expect_column_values_to_be_between("circulating_supply", min_value=18000000, max_value=22000000)
    validator.expect_column_values_to_be_between("developer_score", min_value=0, max_value=100, mostly=0.9)
    validator.expect_column_values_to_be_between("community_score", min_value=0, max_value=100, mostly=0.9)
    validator.expect_column_values_to_be_between("ath", min_value=1000)
    validator.expect_column_values_to_be_between("atl", min_value=0.01)
    validator.expect_column_values_to_be_in_set("valid", [True, False])

    validator.save_expectation_suite()
    return validator.validate()

def summarize_validation_result(result: dict) -> None:
    """
    Print a readable summary of Great Expectations validation results.

    :param result: Validation result dictionary from GE.
    """
    print("\nValidation Summary:\n")

    for r in result["results"]:
        expectation = r["expectation_config"]["expectation_type"]
        kwargs = r["expectation_config"]["kwargs"]
        column = kwargs.get("column", "N/A")
        success = r["success"]

        if expectation == "expect_column_values_to_not_be_null":
            description = f"Column '{column}' should not be null"
        elif expectation == "expect_column_values_to_be_between":
            min_val = kwargs.get("min_value", "-∞")
            max_val = kwargs.get("max_value", "∞")
            description = f"Column '{column}' should be between {min_val} and {max_val}"
        elif expectation == "expect_column_values_to_be_of_type":
            expected_type = kwargs.get("type_", "specified type")
            description = f"Column '{column}' should be of type '{expected_type}'"
        elif expectation == "expect_column_values_to_be_in_set":
            value_set = kwargs.get("value_set", [])
            description = f"Column '{column}' should be in set {value_set}"
        elif expectation == "expect_column_to_exist":
            description = f"Column '{column}' should exist"
        else:
            description = f"{expectation} on column '{column}'"

        status = "Passed" if success else "Failed"
        print(f"- {description} — {status}")
