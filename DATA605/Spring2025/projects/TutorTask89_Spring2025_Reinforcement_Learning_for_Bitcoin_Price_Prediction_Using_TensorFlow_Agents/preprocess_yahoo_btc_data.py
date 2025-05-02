"""
Script to preprocess the data for training and testing the reinforcement learning model.

"""

import pandas as pd
import tensorflow_agents_utils as utils

# Set up the logger for this script
_LOG = utils.logging_setup(log_file="preprocess_yahoo_btc_data.log")

if __name__ == "__main__":
    try:
        train_df = pd.read_csv(
            "data/train_data.csv",
        )
        validation_df = pd.read_csv(
            "data/validation_data.csv",
        )
        test_df = pd.read_csv(
            "data/test_data.csv",
        )
        # Calculate the normalization parameters only from the training data
        normalize_params = utils.calculate_normalization_params(
            train_df, ["Log_Returns", "Price_SMA_20", "Volume_SMA_20", "Volume"]
        )
        # Normalize the training, validation, and test data
        train_df, validation_df, test_df = utils.normalize_data(
            [train_df, validation_df, test_df], normalize_params
        )
        train_df = train_df[
            ["Close", "Log_Returns", "Price_SMA_20", "Volume_SMA_20", "Volume"]
        ]
        validation_df = validation_df[
            ["Close", "Log_Returns", "Price_SMA_20", "Volume_SMA_20", "Volume"]
        ]
        test_df = test_df[
            ["Close", "Log_Returns", "Price_SMA_20", "Volume_SMA_20", "Volume"]
        ]
        utils.save_to_csv(train_df, "data/train_data_normalized.csv")
        utils.save_to_csv(validation_df, "data/validation_data_normalized.csv")
        utils.save_to_csv(test_df, "data/test_data_normalized.csv")
    except Exception as e:
        _LOG.error(f"An error occurred: {e}")
