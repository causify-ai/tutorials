"""
This file contains utlility functions for the project.

Functions include:

- logging_setup: Sets up the logger with customizable handlers for console and file output.
- load_yahoo_data: Fetches historical Bitcoin OHLCV data from Yahoo Finance.
- clean_yahoo_data: Cleans the historical Bitcoin data fetched from Yahoo Finance.
- save_to_csv: Saves the DataFrame to a CSV file.
- localize_to_timezone: Converts a naive datetime or string to a timezone-aware pandas Timestamp.
- split_yahoo_data: Splits the DataFrame into training, testing, and validation sets.
- calculate_features: Computes a suite of features on the DataFrame, including log returns and simple moving averages.
- calculate_normalization_params: Calculates normalization parameters for specified columns in the DataFrame.
- normalize_data: Normalizes the training, validation, and test data using the calculated parameters.
- ingest_bitcoin_data: Loads, cleans, feature-engineers, and returns a DataFrame.
- create_btc_env: Creates a Bitcoin trading environment using the BitcoinTradingEnv class.
- create_q_network: Creates a Q-Network for the DQN agent.
- create_dqn_agent: Creates and initializes a TF-Agents DqnAgent.
- create_collection_policy: Creates an EpsilonGreedyPolicy for data collection.
- create_replay_buffer: Creates a TFUniformReplayBuffer.
- create_data_collection_driver: Creates a DynamicStepDriver for collecting experiences.
- create_training_dataset: Creates a tf.data.Dataset from the replay buffer for training.
- initial_collect: Performs an initial collection of experiences to populate the replay buffer.
- train_one_iteration: Performs one iteration of training the agent.
- calculate_buy_and_hold_performance: Calculates the performance of a Buy & Hold strategy on the given dataset.
- calculate_naive_directional_accuracy: Calculates the directional accuracy of a naive strategy.
"""

import re, os
import logging
from typing import Optional, List, Union, Tuple, Any, Callable

import numpy as np
import pandas as pd
import yfinance as yf
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras import initializers
from tf_agents.environments import tf_py_environment, tf_environment
from tf_agents.specs import tensor_spec
from tf_agents.trajectories import time_step as ts
from tf_agents.agents.dqn import dqn_agent
from tf_agents.policies import epsilon_greedy_policy
from tf_agents.policies import tf_policy
from tf_agents.networks import q_network
from tf_agents.replay_buffers import tf_uniform_replay_buffer
from tf_agents.drivers import dynamic_step_driver
from bitcoin_trading_env import BitcoinTradingEnv
import config


# #############################################################################
# Logging Setup
# #############################################################################
def logging_setup(
    log_level: int = logging.INFO,
    log_file: str = "default.log",
    enable_console: bool = True,
    enable_file: bool = True,
):
    """
    Sets up the logger.

    This function configures the logger with customizable handlers for console and file output.
    Supports all standard logging levels: DEBUG, INFO, WARN, ERROR, and CRITICAL.

    :param log_level: The minimum logging level (DEBUG, INFO, WARN, ERROR, CRITICAL). Defaults to INFO
    :param log_file: The file to which logs will be written. Defaults to 'bitcoin_rl_agent.log'
    :param enable_console: Whether to enable console logging. Defaults to True
    :param enable_file: Whether to enable file logging. Defaults to True
    :return: The logger instance
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    # Clear any existing handlers to avoid duplicates
    if logger.handlers:
        logger.handlers.clear()
    # Define log format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    # Create and add console handler if enabled
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    # Create and add file handler if enabled
    if enable_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    # Ensure logs propagate up to the root logger
    logger.propagate = True
    return logger


# Set up the logger for the utility functions
_LOG = logging_setup()


# #############################################################################
# Data Loading (from Yahoo Finance)
# #############################################################################
def load_yahoo_data(
    ticker: str = "BTC-USD",
    start_date: str = "2014-09-17",
    end_date: str = "2025-04-29",
) -> pd.DataFrame:
    """
    Fetch historical Bitcoin OHLCV data from Yahoo Finance.

    :param ticker: The ticker symbol for the cryptocurrency
    :param start_date: The start date in 'YYYY-MM-DD' format
    :param end_date: The end date in 'YYYY-MM-DD' format
    :return: DataFrame containing the cleaned OHLCV data
    """
    try:
        # Fetch historical data for the given ticker symbol
        btc = yf.Ticker(ticker)
        df = btc.history(start=start_date, end=end_date, interval="1d")
        _LOG.info(f"Fetching data for {ticker} from {start_date} to {end_date}")
        _LOG.info(f"Data shape: {df.shape}")
        return df
    except Exception as e:
        _LOG.error(f"Error fetching data: {e}")
        raise


# #############################################################################
# Data Cleaning (for Yahoo Finance data)
# #############################################################################
def clean_yahoo_data(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Clean the historical Bitcoin data fetched from Yahoo Finance.
    This function removes unnecessary columns and handles missing values.

    :param df: DataFrame containing the historical data
    :return: Cleaned DataFrame
    """
    try:
        # Remove columns not relevant for Bitcoin
        df = df.drop(columns=["Dividends", "Stock Splits"], errors="ignore")
        # Check for missing values
        missing_values = df.isna().any()
        if missing_values.any():
            _LOG.warning(f"Missing values found in DataFrame: {df.isna().sum()}")
            df = df.dropna()
        if df.index.tzinfo is not None:
            _LOG.info(f"DataFrame timezone: {df.index.tzinfo}")
        else:
            _LOG.info("DataFrame has no timezone")
        return df
    except Exception as e:
        _LOG.error(f"Error cleaning data: {e}")
        raise


# #############################################################################
# Save DataFrame to CSV
# #############################################################################
def save_to_csv(df: pd.DataFrame, file_path: str) -> None:
    """
    Save the DataFrame to a CSV file.

    :param df: DataFrame to save
    :param file_path: Path to the CSV file
    :param save_index: Whether to save the DataFrame index to the CSV file
    :return: None
    """
    try:
        os.makedirs("data", exist_ok=True)
        df.to_csv(file_path)
        _LOG.info(f"Data saved to {file_path}")
    except Exception as e:
        _LOG.error(f"Error saving data to CSV: {e}")
        raise


# #############################################################################
# Localize datetime to DataFrame timezone
# #############################################################################
def localize_to_timezone(input_date: str, timezone: str) -> pd.Timestamp:
    """
    Convert a naive datetime or string to a timezone-aware pandas Timestamp.

    :param input_date: The input date, either as a datetime object or a string
    :param timezone: The timezone to localize to (e.g., 'UTC', 'America/New_York')
    :return: A timezone-aware pandas Timestamp
    """
    return pd.to_datetime(input_date).tz_localize(timezone)


# #############################################################################
# Data Split for Training, Validation, and Testing
# #############################################################################
def split_yahoo_data(
    df: pd.DataFrame,
    train_start_date: str = config.TRAIN_START_DATE,
    validation_start_date: str = config.VALIDATION_START_DATE,
    test_start_date: str = config.TEST_START_DATE,
    train_data_path: str = config.TRAIN_DATA_PATH,
    validation_data_path: str = config.VALIDATION_DATA_PATH,
    test_data_path: str = config.TEST_DATA_PATH,
) -> None:
    """
    Split the DataFrame into training, testing, and validation sets.

    :param df: DataFrame containing the historical data
    :param train_start_date: Start date for the training set
    :param validation_start_date: Start date for the validation set
    :param test_start_date: Start date for the testing set
    :param train_data_path: Path to save the training data
    :param validation_data_path: Path to save the validation data
    :param test_data_path: Path to save the testing data
    """
    try:
        # Check if DataFrame index has timezone information
        has_tz = df.index.tzinfo is not None
        if has_tz:
            # If DataFrame has timezone, localize the input dates to match
            train_start_date = localize_to_timezone(train_start_date, df.index.tzinfo)
            validation_start_date = localize_to_timezone(
                validation_start_date, df.index.tzinfo
            )
            test_start_date = localize_to_timezone(test_start_date, df.index.tzinfo)
        else:
            _LOG.info("DataFrame has no timezone")
            # If DataFrame has no timezone, keep dates timezone-naive
            train_start_date = pd.to_datetime(train_start_date)
            validation_start_date = pd.to_datetime(validation_start_date)
            test_start_date = pd.to_datetime(test_start_date)
        _LOG.info(
            f"Train start: {train_start_date}, Validation start: {validation_start_date}, Test start: {test_start_date}"
        )
        # Split the data into training, validation, and testing sets
        train_data = df.loc[
            train_start_date : validation_start_date - pd.Timedelta(days=1)
        ]
        validation_data = df.loc[
            validation_start_date : test_start_date - pd.Timedelta(days=1)
        ]
        test_data = df.loc[test_start_date:]
        _LOG.info(
            f"Train shape: {train_data.shape}, Validation shape: {validation_data.shape}, Test shape: {test_data.shape}"
        )
        # Save the split data to CSV files
        save_to_csv(train_data, train_data_path)
        save_to_csv(validation_data, validation_data_path)
        save_to_csv(test_data, test_data_path)
    except Exception as e:
        _LOG.error(f"Error splitting data: {e}")
        raise


# #############################################################################
# Feature Calculation (Log Returns and SMAs)
# #############################################################################
def calculate_features(
    df: pd.DataFrame,
    price_sma_windows: dict = {"Price_SMA_20": 20},
    volume_sma_windows: dict = {"Volume_SMA_20": 20},
    drop_na: bool = True,
) -> pd.DataFrame:
    """
    Compute a suite of features on the DataFrame, including log returns and simple moving averages.

    :param df: DataFrame with 'Close' and 'Volume' columns and datetime index
    :param price_sma_windows: dict mapping column names to price SMA window sizes, e.g., {'Price_SMA_20': 20}
    :param volume_sma_windows: dict mapping column names to volume SMA window sizes, e.g., {'Volume_SMA_20': 20}
    :param drop_na: whether to drop rows with NaN after feature calculations
    :return: DataFrame with new feature columns added
    """
    try:
        # Create a copy to avoid modifying the original
        df = df.copy()
        # Compute log returns for price
        df["Log_Returns"] = np.log(df["Close"] / df["Close"].shift(1))
        # Compute price SMAs
        for name, window in price_sma_windows.items():
            df[name] = df["Close"].rolling(window=window).mean()
        # Compute volume SMAs
        for name, window in volume_sma_windows.items():
            df[name] = df["Volume"].rolling(window=window).mean()
        # Remove rows with missing values if required
        if drop_na:
            df = df.dropna()
        _LOG.info(f"Data shape after feature calculation: {df.shape}")
        return df
    except Exception as e:
        _LOG.error(f"Error calculating features: {e}")
        raise


# #############################################################################
# Normalization Parameters Calculation
# #############################################################################
def calculate_normalization_params(
    df: pd.DataFrame,
    columns: list,
    method: str = "zscore",
) -> dict:
    """
    Calculate normalization parameters for the specified columns in the DataFrame.

    :param df: DataFrame containing the data
    :param columns: List of columns to calculate parameters for
    :param method: Normalization method ('minmax' or 'zscore')
    :return: Dictionary of normalization parameters for each column
    """
    try:
        params = {}
        if method == "minmax":
            for col in columns:
                min_val = df[col].min()
                max_val = df[col].max()
                params[col] = {"min": min_val, "max": max_val}
                _LOG.info(f"Column {col} - Min: {min_val}, Max: {max_val}")
        elif method == "zscore":
            for col in columns:
                mean = df[col].mean()
                std = df[col].std()
                params[col] = {"mean": mean, "std": std}
                _LOG.info(f"Column {col} - Mean: {mean}, Std: {std}")
        else:
            raise ValueError(f"Unsupported normalization method: {method}")
        return params
    except Exception as e:
        _LOG.error(f"Error calculating normalization parameters: {e}")
        raise


# #############################################################################
# Normalize Data
# #############################################################################
def normalize_data(dataframes: list, params: dict) -> tuple:
    """
    Normalize the training, validation, and test data using the calculated parameters.

    :param dataframes: List of DataFrames to normalize
    :param params: Dictionary of normalization parameters
    :return: Tuple of normalized DataFrames
    """
    try:
        for col, stat in params.items():
            if "min" in stat:
                min_val = stat["min"]
                max_val = stat["max"]
                for df in dataframes:
                    df[col] = (df[col] - min_val) / (max_val - min_val)
            elif "mean" in stat:
                mean = stat["mean"]
                std = stat["std"]
                for df in dataframes:
                    df[col] = (df[col] - mean) / std
        _LOG.info(
            f"Data normalization complete. Data shapes: {[df.shape for df in dataframes]}"
        )
        return dataframes[0], dataframes[1], dataframes[2]
    except Exception as e:
        _LOG.error(f"Error normalizing data: {e}")
        raise


# #############################################################################
# Ingest Data
# #############################################################################
def ingest_bitcoin_data(
    ticker: str = "BTC-USD",
    start_date: str = config.START_DATE,
    end_date: str = config.END_DATE,
    train_start_date: str = config.TRAIN_START_DATE,
    validation_start_date: str = config.VALIDATION_START_DATE,
    test_start_date: str = config.TEST_START_DATE,
    train_data_path: str = config.TRAIN_DATA_PATH,
    validation_data_path: str = config.VALIDATION_DATA_PATH,
    test_data_path: str = config.TEST_DATA_PATH,
):
    """
    Load, clean, feature-engineer, save, split(train, validation, test) the source data and return the DataFrame.

    :param ticker: The ticker symbol for the cryptocurrency
    :param start_date: The start date in 'YYYY-MM-DD' format
    :param end_date: The end date in 'YYYY-MM-DD' format
    :param train_start_date: Start date for the training set
    :param validation_start_date: Start date for the validation set
    :param test_start_date: Start date for the testing set
    :param train_data_path: Path to save the training data
    :param validation_data_path: Path to save the validation data
    :param test_data_path: Path to save the testing data

    :return: DataFrame containing the cleaned and feature-engineered data
    """
    _LOG.info(f"Loading data for {ticker} from {start_date} to {end_date}")
    df = load_yahoo_data(ticker, start_date, end_date)
    df = clean_yahoo_data(df)
    df = calculate_features(df)
    _LOG.info("Ingestion complete: features calculated")
    # Save the data to CSV
    save_to_csv(df, config.SRC_DATA_PATH)
    _LOG.info(f"Data saved to {config.SRC_DATA_PATH}")
    # Split the data into training, validation, and test sets
    split_yahoo_data(
        df,
        train_start_date,
        validation_start_date,
        test_start_date,
        train_data_path,
        validation_data_path,
        test_data_path,
    )
    _LOG.info(
        f"Data split into training, validation, and test sets. "
        f"Train shape: {df.shape}, Validation shape: {df.shape}, Test shape: {df.shape}"
    )
    _LOG.info("Data ingestion complete")
    return df


# #############################################################################
# Create Bitcoin Trading Environment
# #############################################################################
def create_btc_env(
    data_path: str,
    window_size: int = 20,
    fee: float = 0.001,
    feature_columns: Optional[List[str]] = None,
    wrap_in_tf_env: bool = True,
) -> Union[BitcoinTradingEnv, tf_py_environment.TFPyEnvironment]:
    _LOG.info(f"Attempting to create BitcoinTradingEnv with data from: {data_path}")
    try:
        df = pd.read_csv(data_path)
        _LOG.info(
            f"Successfully loaded data. Shape: {df.shape}, Columns: {df.columns.tolist()}"
        )
    except Exception as e:
        _LOG.error(f"Failed to load data from {data_path}: {e}")
        raise
    if "Close" not in df.columns:
        _LOG.error(
            f"'Close' column not found in {data_path}. It is required for reward calculation."
        )
        raise ValueError(f"'Close' column not found in {data_path}")
    if feature_columns is None:
        default_features = ["Log_Returns", "Price_SMA_20", "Volume_SMA_20", "Volume"]
        feature_columns = [col for col in default_features if col in df.columns]
        if not feature_columns:
            _LOG.error(
                f"No default feature columns ({default_features}) found in {data_path}."
            )
            raise ValueError("No feature columns available for the environment.")
        _LOG.info(
            f"Using automatically determined feature columns for observation: {feature_columns}"
        )
    else:
        missing_cols = [col for col in feature_columns if col not in df.columns]
        if missing_cols:
            _LOG.error(
                f"Specified feature_columns not found in DataFrame: {missing_cols}"
            )
            raise ValueError(f"Missing feature columns: {missing_cols}")
        _LOG.info(f"Using specified feature columns for observation: {feature_columns}")
    py_env = BitcoinTradingEnv(
        df=df,
        window_size=window_size,
        fee=fee,
        feature_columns=feature_columns,
    )
    _LOG.info(
        f"BitcoinTradingEnv (PyEnvironment) created successfully. Observation Spec: {py_env.observation_spec()}, Action Spec: {py_env.action_spec()}"
    )
    if wrap_in_tf_env:
        tf_env = tf_py_environment.TFPyEnvironment(py_env)
        _LOG.info("Successfully wrapped environment in TFPyEnvironment.")
        return tf_env
    return py_env


# #############################################################################
# Create Q-Network
# #############################################################################
def create_q_network(
    observation_spec: tensor_spec.TensorSpec,
    action_spec: tensor_spec.BoundedTensorSpec,
    fc_layer_params: Tuple[int, ...] = config.FC_LAYER_PARAMS,
    activation_fn: Any = tf.keras.activations.relu,
    kernel_initializer: tf.keras.initializers.Initializer = initializers.VarianceScaling(
        scale=config.KERNEL_INIT_SCALE,
        mode=config.KERNEL_INIT_MODE,
        distribution=config.KERNEL_INIT_DISTRIBUTION,
    ),
    dropout_rate_for_fc_layers: Optional[float] = config.DROPOUT_RATE,
) -> q_network.QNetwork:
    """
    Creates a Q-Network for the DQN agent.

    Handles 2D observations by flattening before FC layers. Includes options for
    kernel initializer and dropout after each FC layer.

    Args:
        observation_spec: A tf.TensorSpec for observations.
        action_spec: A tf.TensorSpec for actions.
        fc_layer_params: Tuple of units for each fully connected hidden layer.
        activation_fn: Activation function for hidden layers.
        kernel_initializer: Initializer for kernel weights of dense layers.
        dropout_rate_for_fc_layers: Dropout rate to apply after each FC layer.
                                     If None, no dropout is applied.

    Returns:
        An instance of tf_agents.networks.q_network.QNetwork.
    """
    dropout_layer_params_for_qnetwork: Optional[Tuple[float, ...]] = None
    if dropout_rate_for_fc_layers is not None and fc_layer_params:
        dropout_layer_params_for_qnetwork = tuple(
            [dropout_rate_for_fc_layers] * len(fc_layer_params)
        )
    q_net = q_network.QNetwork(
        input_tensor_spec=observation_spec,
        action_spec=action_spec,
        fc_layer_params=fc_layer_params,
        activation_fn=activation_fn,
        kernel_initializer=kernel_initializer,
        dropout_layer_params=dropout_layer_params_for_qnetwork,
    )
    return q_net


# #############################################################################
# Create DQN Agent
# #############################################################################
def create_dqn_agent(
    time_step_spec: ts.TimeStep,
    action_spec: tensor_spec.BoundedTensorSpec,
    q_net: q_network.QNetwork,
    optimizer: tf.keras.optimizers.Optimizer,
    train_step_counter: tf.Variable,
    gamma: float = config.GAMMA,
    target_update_tau: Optional[float] = config.TARGET_UPDATE_TAU,
    td_errors_loss_fn: Any = dqn_agent.common.element_wise_huber_loss,
    gradient_clipping: Optional[float] = config.GRADIENT_CLIPPING_NORM,
) -> dqn_agent.DqnAgent:
    """
    Creates and initializes a TF-Agents DqnAgent.

    Note on Exploration: The DqnAgent itself computes a greedy policy based on Q-values.
    Exploration strategies (e.g., epsilon-greedy with annealing epsilon) are typically
    implemented by wrapping the agent's `policy` with a collection policy like
    `tf_agents.policies.epsilon_greedy_policy.EpsilonGreedyPolicy` during data collection.
    The `epsilon_greedy` parameter of the DqnAgent constructor sets an initial value for
    a simple built-in epsilon-greedy mechanism but is often superseded by an explicit
    exploration policy wrapper during training setup.
    Args:
        time_step_spec: A tf_agents.trajectories.time_step.TimeStep spec.
        action_spec: A tf.TensorSpec for actions.
        q_net: The Q-Network instance.
        optimizer: A tf.keras.optimizers.Optimizer instance.
        train_step_counter: A tf.Variable to count training steps.
        gamma: Discount factor for future rewards.
        target_update_tau: (Optional) The soft update factor (tau). If None, hard updates are used.
        td_errors_loss_fn: Loss function for TD errors.
        gradient_clipping: (Optional) If not None, gradients are clipped to this norm.
                           Defaults to 1.0.

    Returns:
        An initialized instance of tf_agents.agents.dqn.dqn_agent.DqnAgent.
    """
    target_update_period = (
        config.TARGET_UPDATE_PERIOD_WITH_TAU
        if target_update_tau is not None
        else config.TARGET_UPDATE_PERIOD_WITHOUT_TAU
    )
    agent = dqn_agent.DqnAgent(
        time_step_spec=time_step_spec,
        action_spec=action_spec,
        q_network=q_net,
        optimizer=optimizer,
        td_errors_loss_fn=td_errors_loss_fn,
        gamma=gamma,
        target_update_period=target_update_period,
        target_update_tau=target_update_tau,
        train_step_counter=train_step_counter,
        gradient_clipping=gradient_clipping,
        # Epsilon for exploration will be handled by a wrapper policy during data collection.
    )
    agent.initialize()
    return agent


# #############################################################################
# Create Epsilon Greedy Policy for Data Collection
# #############################################################################
def create_collection_policy(
    tf_agent: dqn_agent.DqnAgent,
    epsilon_fn: Callable[[], tf.Tensor],
) -> epsilon_greedy_policy.EpsilonGreedyPolicy:
    """
    Creates an EpsilonGreedyPolicy for data collection.

    Args:
        tf_agent: The TF-Agents DQN agent whose greedy policy will be wrapped.
        epsilon_fn: A callable (e.g., a lambda function or a tf.Variable.value)
                    that returns the current epsilon value (a tf.Tensor).
                    This allows for dynamic epsilon annealing.

    Returns:
        An EpsilonGreedyPolicy instance.
    """
    collect_policy = epsilon_greedy_policy.EpsilonGreedyPolicy(
        policy=tf_agent.policy,  # The agent's greedy policy for exploitation
        epsilon=epsilon_fn,  # Epsilon for exploration
    )
    _LOG.info(
        "EpsilonGreedyPolicy created for collection. Initial epsilon will be determined by epsilon_fn()."
    )
    return collect_policy


# #############################################################################
# Create Replay Buffer for Experience Replay
# #############################################################################
def create_replay_buffer(
    tf_agent: dqn_agent.DqnAgent,
    environment_batch_size: int,
    replay_buffer_capacity: int = config.REPLAY_BUFFER_CAPACITY,
) -> tf_uniform_replay_buffer.TFUniformReplayBuffer:
    """
    Creates a TFUniformReplayBuffer.

    Args:
        tf_agent: The TF-Agent whose data spec will be used.
        environment_batch_size: The batch size of the environment (typically 1).
        replay_buffer_capacity: The maximum number of experiences to store.

    Returns:
        An instance of TFUniformReplayBuffer.
    """
    replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(
        data_spec=tf_agent.collect_data_spec,
        batch_size=environment_batch_size,
        max_length=replay_buffer_capacity,
    )
    _LOG.info(f"TFUniformReplayBuffer created with capacity: {replay_buffer_capacity}")
    return replay_buffer


# #############################################################################
# Create Data Collection Driver for Experience Collection
# #############################################################################
def create_data_collection_driver(
    train_tf_env: tf_environment.TFEnvironment,
    collect_policy: tf_policy.TFPolicy,
    replay_buffer: tf_uniform_replay_buffer.TFUniformReplayBuffer,
    steps_to_collect: int,
) -> dynamic_step_driver.DynamicStepDriver:
    """
    Creates a DynamicStepDriver for collecting experiences.

    Args:
        train_tf_env: The TF-Environment to collect experiences from.
        collect_policy: The policy to use for action selection during collection.
        replay_buffer: The replay buffer to store collected experiences.
        steps_to_collect: The number of steps to collect when driver.run() is called.

    Returns:
        An instance of DynamicStepDriver.
    """
    replay_observer = [replay_buffer.add_batch]
    driver = dynamic_step_driver.DynamicStepDriver(
        train_tf_env,
        collect_policy,
        observers=replay_observer,
        num_steps=steps_to_collect,
    )
    _LOG.info(f"DynamicStepDriver created to collect {steps_to_collect} steps per run.")
    return driver


# #############################################################################
# Create Training Dataset from Replay Buffer
# #############################################################################
def create_training_dataset(
    replay_buffer: tf_uniform_replay_buffer.TFUniformReplayBuffer,
    tf_agent: dqn_agent.DqnAgent,  # Used for train_sequence_length
    batch_size: int = config.BATCH_SIZE,
    num_parallel_calls: int = tf.data.AUTOTUNE,
    prefetch_buffer_size: int = tf.data.AUTOTUNE,
) -> tf.data.Dataset:
    """
    Creates a tf.data.Dataset from the replay buffer for training.

    Args:
        replay_buffer: The replay buffer to sample from.
        tf_agent: The agent, used to determine train_sequence_length.
        batch_size: The batch size for training samples.
        num_parallel_calls: Number of parallel calls for dataset processing.
        prefetch_buffer_size: Buffer size for prefetching data.

    Returns:
        A tf.data.Dataset instance.
    """

    dataset_num_steps = tf_agent.train_sequence_length
    if dataset_num_steps is None:  # Should default to 1 for DqnAgent
        dataset_num_steps = 1
        _LOG.warning(
            "Agent train_sequence_length is None, defaulting dataset num_steps to 1."
        )

    dataset = replay_buffer.as_dataset(
        num_parallel_calls=num_parallel_calls,
        sample_batch_size=batch_size,
        num_steps=dataset_num_steps,  # For DQN, this effectively samples single transitions (T=1)
        # The agent then constructs (s,a,r,s') from these.
    ).prefetch(prefetch_buffer_size)
    _LOG.info(
        f"Training dataset created from replay buffer: "
        f"batch_size={batch_size}, num_steps_in_sample={dataset_num_steps}"
    )
    return dataset


# #############################################################################
# Initial Collection of Experiences
# #############################################################################
def initial_collect(
    initial_collect_driver: dynamic_step_driver.DynamicStepDriver,
    replay_buffer: tf_uniform_replay_buffer.TFUniformReplayBuffer,
) -> None:
    """
    Performs an initial collection of experiences to populate the replay buffer.

    Args:
        initial_collect_driver: The driver configured with a policy (e.g., random)
                                and number of steps for initial collection.
        replay_buffer: The replay buffer to populate.
    """
    _LOG.info("Starting initial collection of experiences...")
    initial_collect_driver.run()
    _LOG.info(
        f"Initial collection complete. Replay buffer now contains "
        f"{replay_buffer.num_frames()} frames."
    )


# #############################################################################
# Train One Iteration of the Agent
# #############################################################################
def train_one_iteration(
    dataset_iterator: Any,  # Iterator for the training dataset
    tf_agent: dqn_agent.DqnAgent,
) -> tf.Tensor:  # Returns the training loss
    """
    Performs one iteration of training the agent.

    Args:
        dataset_iterator: An iterator for the tf.data.Dataset providing training batches.
        tf_agent: The agent to be trained.
        train_step_counter: A tf.Variable tracking the number of training steps.

    Returns:
        The training loss for this iteration.
    """
    experience, _ = next(dataset_iterator)  # Get a batch of experience
    batch_size = config.BATCH_SIZE
    weights = tf.constant(1.0 / batch_size, shape=(batch_size,), dtype=tf.float32)
    loss_info = tf_agent.train(experience, weights=weights)
    return loss_info.loss


# #############################################################################
# Baseline Strategy Evaluation
# #############################################################################
def calculate_buy_and_hold_performance(
    data_path: str,
    initial_capital: float = 10000.0,
    date_column: str = "Date",
    open_column: str = "Open",
    close_column: str = "Close",
    visualize: bool = True,
) -> Tuple[float, pd.DataFrame, float]:
    """
    Calculates the performance of a Buy & Hold strategy on the given dataset.

    The strategy buys at the 'Open' price of the first day (of the provided data_path)
    and holds until the 'Close' price of the last day (of the provided data_path).
    The input data should contain original, unscaled prices.

    Args:
        data_path: Path to the CSV data file (e.g., your raw test split: config.TEST_DATA_PATH).
        initial_capital: The initial capital to simulate the investment.
        date_column: The name of the column containing date information.
        open_column: The name of the column containing daily open prices.
        close_column: The name of the column containing daily close prices.
        visualize: Whether to plot portfolio value over time.

    Returns:
        A tuple containing:
            - final_portfolio_value (float): The value of the portfolio at the end.
            - portfolio_history (pd.DataFrame): DataFrame with 'Timestamp' and 'PortfolioValue'.
            - total_return_percentage (float): The total percentage return.
    """
    _LOG.info(f"Calculating Buy & Hold performance for data: {data_path}")
    try:
        df = pd.read_csv(data_path)
        if df.empty:
            _LOG.warning(f"Data at {data_path} is empty. Cannot calculate Buy & Hold.")
            return (
                initial_capital,
                pd.DataFrame({"Timestamp": [], "PortfolioValue": []}),
                0.0,
            )
        required_cols = {date_column, open_column, close_column}
        if not required_cols.issubset(df.columns):
            missing = required_cols - set(df.columns)
            _LOG.error(f"Required columns {missing} not found in {data_path}.")
            raise ValueError(
                f"DataFrame must contain specified date, open, and close columns. Missing: {missing}"
            )
        df["Timestamp"] = pd.to_datetime(df[date_column])
        df.sort_values(by="Timestamp", inplace=True)
        df.reset_index(drop=True, inplace=True)
        buy_ts = df["Timestamp"].iloc[0]
        sell_ts = df["Timestamp"].iloc[-1]
        buy_price = df[open_column].iloc[0]
        if pd.isna(buy_price) or buy_price <= 0:
            _LOG.error(f"Invalid buy price ({buy_price}) at the start of {data_path}.")
            raise ValueError("Invalid or missing buy price at the start of the data.")
        num_coins = initial_capital / buy_price
        _LOG.info(
            f"Buy & Hold: Buying {num_coins:.6f} BTC at {buy_price:.2f} on {buy_ts.strftime('%Y-%m-%d')}"
        )
        portfolio_history_values = num_coins * df[close_column]
        portfolio_history_df = pd.DataFrame(
            {"Timestamp": df["Timestamp"], "PortfolioValue": portfolio_history_values}
        )
        final_portfolio_value = portfolio_history_values.iloc[-1]
        sell_price = df[close_column].iloc[-1]
        _LOG.info(
            f"Buy & Hold: Holding until {sell_ts.strftime('%Y-%m-%d')}. Last close price: {sell_price:.2f}. Final value: {final_portfolio_value:.2f}"
        )
        total_return_percentage = (
            (final_portfolio_value - initial_capital) / initial_capital
        ) * 100
        _LOG.info(f"Buy & Hold: Total Return: {total_return_percentage:.2f}%")
        if visualize:
            plt.figure(figsize=(10, 5))
            plt.plot(
                portfolio_history_df["Timestamp"],
                portfolio_history_df["PortfolioValue"],
            )
            plt.title("Buy‑&‑Hold Portfolio Value Over Time")
            plt.xlabel("Date")
            plt.ylabel("Portfolio Value (USD)")
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()
        return final_portfolio_value, portfolio_history_df, total_return_percentage
    except FileNotFoundError:
        _LOG.error(f"Data file not found: {data_path}")
        raise
    except Exception as e:
        _LOG.error(
            f"Error calculating Buy & Hold performance for {data_path}: {e}",
            exc_info=True,
        )
        raise


# #############################################################################
# Naive Prediction Baselines
# #############################################################################
def calculate_naive_directional_accuracy(
    data_path: str,
    prediction_type: str,  # "always_up" or "always_down"
    date_column: str = "Date",
    close_column: str = "Close",
    visualize: bool = True,
) -> Tuple[float, int, int]:
    """
    Calculates the accuracy of a naive 'Always Predict Up' or 'Always Predict Down' strategy.

    Args:
        data_path: Path to the CSV data file.
        prediction_type: Specifies the naive strategy. Must be "always_up" or "always_down".
        date_column: The name of the column containing date/timestamp information.
        close_column: The name of the column containing daily close prices.
        visualize: Whether to show a bar plot comparing the two naïve baselines.

    Returns:
        A tuple containing:
            - accuracy (float): The directional accuracy (0.0 to 1.0).
            - num_correct_predictions (int): Number of correctly predicted days.
            - total_prediction_days (int): Total number of days used for prediction.
    """
    _LOG.info(f"Calculating Naive '{prediction_type}' accuracy for data: {data_path}")
    if prediction_type not in ["always_up", "always_down"]:
        _LOG.error(
            f"Invalid prediction_type: {prediction_type}. Must be 'always_up' or 'always_down'."
        )
        raise ValueError("Invalid prediction_type for naive accuracy.")
    try:
        df = pd.read_csv(data_path)
        if df.empty or len(df) < 2:
            _LOG.warning(
                f"Data at {data_path} is too short (<2 rows) to calculate directional accuracy."
            )
            return 0.0, 0, 0
        required_cols = {date_column, close_column}
        if not required_cols.issubset(df.columns):
            missing = required_cols - set(df.columns)
            _LOG.error(
                f"Required columns {missing} not found in {data_path} for naive accuracy."
            )
            raise ValueError(
                f"DataFrame must contain specified date and close columns. Missing: {missing}"
            )
        df["Timestamp"] = pd.to_datetime(df[date_column])
        df.sort_values(by="Timestamp", inplace=True)
        df.reset_index(drop=True, inplace=True)
        df["PriceChange"] = df[close_column].diff()
        df_comparable = df.dropna(subset=["PriceChange"])
        if df_comparable.empty:
            _LOG.warning(f"No comparable days after diff() for data: {data_path}")
            return 0.0, 0, 0
        total_prediction_days = len(df_comparable)
        if prediction_type == "always_up":
            num_correct_predictions = (df_comparable["PriceChange"] > 0).sum()
        else:  # "always_down"
            num_correct_predictions = (df_comparable["PriceChange"] < 0).sum()
        accuracy = num_correct_predictions / total_prediction_days
        _LOG.info(
            f"Naive '{prediction_type}' Accuracy: {accuracy:.2%} "
            f"({num_correct_predictions}/{total_prediction_days} days)"
        )
        # Visualize the results
        if visualize:
            other_type = (
                "always_down" if prediction_type == "always_up" else "always_up"
            )
            other_acc, _, _ = calculate_naive_directional_accuracy(
                data_path,
                other_type,
                date_column=date_column,
                close_column=close_column,
                visualize=False,
            )
            plt.figure(figsize=(6, 4))
            plt.bar(
                ["Always Up", "Always Down"],
                [
                    accuracy if prediction_type == "always_up" else other_acc,
                    accuracy if prediction_type == "always_down" else other_acc,
                ],
                color=["tab:blue", "tab:orange"],
            )
            plt.title("Naïve Directional Accuracy Baselines")
            plt.ylabel("Accuracy")
            plt.ylim(0, 1)
            for idx, val in enumerate(
                [
                    accuracy if prediction_type == "always_up" else other_acc,
                    accuracy if prediction_type == "always_down" else other_acc,
                ]
            ):
                plt.text(idx, val + 0.02, f"{val:.2%}", ha="center")
            plt.tight_layout()
            plt.show()
        return accuracy, num_correct_predictions, total_prediction_days
    except FileNotFoundError:
        _LOG.error(f"Data file not found for naive accuracy: {data_path}")
        raise
    except Exception as e:
        _LOG.error(
            f"Error calculating naive directional accuracy for {data_path}: {e}",
            exc_info=True,
        )
        raise


# #############################################################################
# Visualization (Line Chart)
# #############################################################################
def plot_series(
    df: pd.DataFrame,
    y_col: str,
    x_col: Optional[str] = None,
    title: Optional[str] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
) -> None:
    """
    Plot a line chart of one column against another from a DataFrame, using
    either a column or the DataFrame’s index for the x-axis.

    :param df: DataFrame containing the data.
    :param x_col: Column name for the x-axis. If None, or if not found in
        df.columns but matches df.index.name, uses df.index instead.
    :param y_col: Column name for the y-axis.
    :param title: Title of the plot.
    :param xlabel: Label for the x-axis.
    :param ylabel: Label for the y-axis.

    :return: None
    """
    if x_col is None:
        x = df.index
        x_label = xlabel or (df.index.name or "index")
    elif x_col in df.columns:
        if not pd.api.types.is_datetime64_any_dtype(df[x_col]):
            x = pd.to_datetime(df[x_col])
        else:
            x = df[x_col]
        x_label = xlabel or x_col
    elif df.index.name == x_col:
        x = df.index
        x_label = xlabel or x_col
    else:
        raise ValueError(
            f"x_col '{x_col}' not found in DataFrame columns or index name"
        )
    if y_col not in df.columns:
        raise ValueError(f"y_col '{y_col}' not found in DataFrame columns")
    y = df[y_col]
    y_label = ylabel or y_col
    plt.figure()
    plt.plot(x, y, label=y_col)
    plt.title(title or f"{y_col} vs {x_label}")
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.tight_layout()
    plt.show()


# #############################################################################
# Model selection – pick the highest‑reward policy in a folder
# #############################################################################
def get_best_policy_path(policy_root: str) -> str:
    """
    Scan policy_root for sub-folders named
    ``policy_step_<step>_reward_<reward>`` (optionally ending in .zip)
    and return the path of the folder with the highest reward.

    :param policy_root: Directory that contains saved policy folders.
    :return: Path to the best-reward policy folder.
    """
    pattern = re.compile(r"policy_step_(\d+)_reward_([-+]?[0-9]*\.?[0-9]+)(?:\.zip)?$")
    best_reward = -float("inf")  #  so any real reward is greater
    best_path: str | None = None
    for name in os.listdir(policy_root):
        match = pattern.match(name)
        if match:
            reward = float(match.group(2))
            if reward > best_reward:
                best_reward = reward
                best_path = os.path.join(policy_root, name)
    if best_path is None:
        raise FileNotFoundError(f"No policies matching pattern found in {policy_root}")
    _LOG.info(
        f"Best policy found: {os.path.basename(best_path)} (reward {best_reward:.5f})"
    )
    return best_path
