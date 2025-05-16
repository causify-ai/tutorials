"""
Configuration file for the project.
Contains hyperparameters and settings for data, environment, agent, and training.
"""

from typing import Optional, Tuple, Union


# #############################################################################
# Dates
# #############################################################################
# Ingestion window
START_DATE: str = "2014-09-17"
END_DATE: str = "2025-04-29"
# Data-split boundaries
TRAIN_START_DATE: str = "2014-09-17"
VALIDATION_START_DATE: str = "2022-02-21"
TEST_START_DATE: str = "2024-01-01"

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

POLICY_SAVE_PATH: str = "policy"  # Directory to save the trained policy


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
FEE = 0.001  # Transaction fee for buy/sell actions

# #############################################################################
# Seed
# #############################################################################
RANDOM_SEED: int = 42  # Random seed for reproducibility

# #############################################################################
# Q-Network Hyperparameters
# #############################################################################
FC_LAYER_PARAMS: Tuple[int, ...] = (128, 64)
KERNEL_INIT_SCALE: float = 2.0
KERNEL_INIT_MODE: str = "fan_in"
KERNEL_INIT_DISTRIBUTION: str = "truncated_normal"
# Set to a float (e.g., 0.1, 0.2) to enable dropout, or None to disable.
# If a float, dropout layers with this rate will be added after each FC layer.
DROPOUT_RATE: Optional[float] = None  # Example: 0.1 for 10% dropout

# #############################################################################
# DQN Agent Hyperparameters
# #############################################################################
LEARNING_RATE: float = 1e-5  # Learning rate for the optimizer (Adam)
GAMMA: float = 0.99  # Discount factor for future rewards
TARGET_UPDATE_PERIOD: int = 100
GRADIENT_CLIPPING_NORM: Union[float, None] = (
    1.0  # Gradient clipping norm (None to disable)
)
# If TARGET_UPDATE_TAU is set, soft updates are used.
# If TARGET_UPDATE_TAU is None, hard updates are used with TARGET_UPDATE_PERIOD.
TARGET_UPDATE_TAU: Union[float, None] = 0.005
TARGET_UPDATE_PERIOD_WITH_TAU: int = 1
TARGET_UPDATE_PERIOD_WITHOUT_TAU: int = (
    100  # Number of steps before updating the target Q-network
)

# #############################################################################
# Replay Buffer Hyperparameters
# #############################################################################
REPLAY_BUFFER_CAPACITY: int = (
    100000  # Maximum number of experiences in the replay buffer
)

# #############################################################################
# Data Collection Hyperparameters
# #############################################################################
INITIAL_COLLECT_STEPS: int = (
    1000  # Number of steps to fill buffer before training starts
)
COLLECT_STEPS_PER_ITERATION: int = (
    1  # Number of steps to collect in env per training iteration
)
BATCH_SIZE: int = 64  # Batch size for sampling from replay buffer for training

# #############################################################################
# Training Loop Hyperparameters
# #############################################################################
NUM_TRAINING_ITERATIONS: int = 10000  # Example: Total agent.train() calls
LOG_INTERVAL: int = 200  # Log training loss every N iterations

# #############################################################################
# Epsilon Greedy Exploration Hyperparameters
# #############################################################################
INITIAL_EPSILON: float = (
    1.0  # Starting epsilon for exploration for initial collection policy setup
)
MIN_EPSILON: float = 0.01  # Minimum epsilon for exploration
EPSILON_DECAY_TRAINING_STEPS: int = int(NUM_TRAINING_ITERATIONS * 0.7)

# #############################################################################
# Evaluation Hyperparameters
# #############################################################################
EVAL_INTERVAL: int = 1000  # e.g., Evaluate every 1000 training steps
NUM_EVAL_EPISODES: int = 5  # Number of episodes to evaluate the agent
