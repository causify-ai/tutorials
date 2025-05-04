"""
Script to preprocess the data for training and testing the reinforcement learning model.

"""

import pandas as pd
import tensorflow_agents_utils as utils
import config

# Set up the logger for this script
_LOG = utils.logging_setup(log_file="preprocess_yahoo_btc_data.log")

if __name__ == "__main__":
    try:
        train_df = pd.read_csv(
            config.TRAIN_DATA_PATH,
        )
        validation_df = pd.read_csv(
            config.VALIDATION_DATA_PATH,
        )
        test_df = pd.read_csv(
            config.TEST_DATA_PATH,
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
        utils.save_to_csv(train_df, config.NORM_TRAIN_DATA_PATH)
        utils.save_to_csv(validation_df, config.NORM_VALIDATION_DATA_PATH)
        utils.save_to_csv(test_df, config.NORM_TEST_DATA_PATH)
    except Exception as e:
        _LOG.error(f"An error occurred: {e}")
