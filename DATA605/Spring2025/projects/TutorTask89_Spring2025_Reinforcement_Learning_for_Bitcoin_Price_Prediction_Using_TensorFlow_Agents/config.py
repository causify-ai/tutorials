"""
Configuration file for the project.
Contains hyperparameters and settings for data, environment, agent, and training.
"""

from typing import Optional, Tuple
from tensorflow.keras import initializers
import tensorflow as tf

# #############################################################################
# Data Configuration
# #############################################################################
SRC_DATA_PATH: str = "data/raw_data.csv"
TRAIN_DATA_PATH: str = "data/train_data.csv"
VALIDATION_DATA_PATH: str = "data/validation_data.csv"
TEST_DATA_PATH: str = "data/test_data.csv"
NORM_TRAIN_DATA_PATH: str = "data/train_data_normalized.csv"
NORM_VALIDATION_DATA_PATH: str = "data/validation_data_normalized.csv"
NORM_TEST_DATA_PATH: str = "data/test_data_normalized.csv"


# #############################################################################
# Environment Configuration
# #############################################################################
WINDOW_SIZE: int = 20  # Number of time steps to consider for the environment
NUM_ACTIONS: int = 3  # Number of actions (buy, sell, hold)
NUM_MARKET_FEATURES: int = 4  # Number of market features (e.g., price, volume, etc.)
NUM_POSITION_FEATURES: int = 1  # Number of position features (e.g., current position)
NUM_FEATURES_IN_OBSERVATION: int = (
    NUM_MARKET_FEATURES + NUM_POSITION_FEATURES
)  # Total number of features in the observation space

# #############################################################################
# Q-Network Hyperparameters
# #############################################################################
FC_LAYER_PARAMS: Tuple[int, ...] = (128, 64)
KERNEL_INITIALIZER: tf.keras.initializers.Initializer = initializers.VarianceScaling(
    scale=2.0, mode="fan_in", distribution="truncated_normal"
)
# Set to a float (e.g., 0.1, 0.2) to enable dropout, or None to disable.
# If a float, dropout layers with this rate will be added after each FC layer.
DROPOUT_RATE: Optional[float] = None  # Example: 0.1 for 10% dropout

# #############################################################################
# DQN Agent Hyperparameters
# #############################################################################
LEARNING_RATE: float = 1e-4
GAMMA: float = 0.99
TARGET_UPDATE_PERIOD: int = 100
