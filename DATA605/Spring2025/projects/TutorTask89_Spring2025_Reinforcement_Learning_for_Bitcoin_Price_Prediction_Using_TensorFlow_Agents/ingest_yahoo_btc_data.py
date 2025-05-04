"""
Script for loading and preparing Bitcoin price data from Yahoo Finance.

Historical data is fetched using the yfinance library, cleaned, and saved to a CSV file.
"""

import tensorflow_agents_utils as utils
import config

# Set up the logger for this script
_LOG = utils.logging_setup(log_file="ingest_yahoo_btc_data.log")

if __name__ == "__main__":
    try:
        data = utils.load_yahoo_data(
            ticker="BTC-USD",
            start_date="2014-09-17",
            end_date="2025-04-29",
        )
        cleaned_df = utils.clean_yahoo_data(data)
        features_df = utils.calculate_features(cleaned_df)
        utils.save_to_csv(features_df, config.SRC_DATA_PATH)
        utils.split_yahoo_data(features_df)
    except Exception as e:
        _LOG.error(f"An error occurred: {e}")
