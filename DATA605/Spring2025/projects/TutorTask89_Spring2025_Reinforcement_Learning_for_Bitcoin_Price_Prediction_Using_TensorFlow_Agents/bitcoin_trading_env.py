"""
Custom environment for Bitcoin trading using TensorFlow Agents.

"""

import numpy as np
import pandas as pd
from typing import List, Optional
from tf_agents.environments import py_environment
from tf_agents.specs import array_spec
from tf_agents.trajectories import time_step as ts


class BitcoinTradingEnv(py_environment.PyEnvironment):
    """
    Custom environment for Bitcoin trading using TensorFlow Agents.
    """

    def __init__(
        self,
        df: pd.DataFrame,
        window_size: int = 20,
        fee: float = 0.001,
        feature_columns: Optional[List[str]] = None,
    ):
        """
        Initializes the Bitcoin trading environment.

        :param df: DataFrame containing the Bitcoin price data.
        :param window_size: Size of the observation window.
        :param fee: Transaction fee for buying/selling Bitcoin per trade (fraction of the trade amount).
        :param feature_columns: (Optional) List of feature columns to be used in the observation space.
        """
        super().__init__()
        self._df: pd.DataFrame = df
        self.window_size: int = window_size
        self.fee: float = fee
        # Internal State
        self._current_tick: int = self.window_size - 1
        self._position = 0  #  0=flat, +1=long, -1=short
        # Specifiications
        self.feature_columns: List[str] = feature_columns or [
            "Log_Returns",
            "Price_SMA_20",
            "Volume_SMA_20",
            "Volume",
        ]
        self.num_price_feats: int = len(self.feature_columns)
        num_feats = (
            self.num_price_feats + 1
        )  # +1 for the position {-1: short, 0: flat, +1: long}
        # Observation space
        self._observation_spec = array_spec.BoundedArraySpec(
            shape=(self.window_size, num_feats),
            dtype=np.float32,
            minimum=-np.inf,
            maximum=np.inf,
            name="observation",
        )
        # Action space
        self._action_spec = array_spec.BoundedArraySpec(
            shape=(),
            dtype=np.int32,
            minimum=0,
            maximum=2,
            name="action",
        )

    def action_spec(self) -> array_spec.BoundedArraySpec:
        """
        Returns the action specification for the environment.
        The action space consists of three discrete actions:
        0: Sell/Go Short, 1: Hold/Do Nothing, 2: Buy/Go Long.
        """
        return self._action_spec

    def observation_spec(self) -> array_spec.BoundedArraySpec:
        """
        Returns the observation specification for the environment.
        The observation space consists of a window of features and the current position.
        """
        return self._observation_spec

    def _reset(self) -> ts.TimeStep:
        """
        Resets the environment to the initial state.
        """
        self._current_tick = self.window_size - 1
        self._position = 0
        return ts.restart(self._get_observation())

    def _step(self, action: int) -> ts.TimeStep:
        """
        Takes a step in the environment based on the action take
        0 = Sell/Go Short
        1 = Hold/do nothing
        2 = Buy/Go Long
        """
        prev_pos = self._position
        # Update the position based on the action taken
        if action == 0:
            self._position = -1
        elif action == 2:
            self._position = 1
        # action == 1: position remains unchanged (Hold)
        # Compute the reward using price log-returns only if not at the last tick
        if self._current_tick + 1 < len(self._df):
            price_t = self._df.loc[self._current_tick, "Close"]
            price_tp1 = self._df.loc[self._current_tick + 1, "Close"]
            log_ret = np.log(price_tp1 / price_t)
        else:
            # Last step, use a zero return
            log_ret = 0.0
        # Calculate the trading cost if position changed
        trade_cost = abs(self._position - prev_pos) * self.fee
        # Calculate reward (position effect on returns - trading cost)
        reward = (self._position * log_ret) - trade_cost
        self._current_tick += 1
        # Check if the episode is done
        if self._current_tick >= len(self._df) - 1:
            return ts.termination(self._get_observation(), reward)
        # Next Observation and transition
        return ts.transition(self._get_observation(), reward=reward, discount=1.0)

    def _get_observation(self) -> np.ndarray:
        """
        Returns an array of shape (window_size, num_price_feats+1):
          - First window_size rows of your feature block (padded by edge-values if needed)
          - A constant column of self._position
        """
        start = self._current_tick - self.window_size + 1
        end = self._current_tick + 1
        block = (
            self._df[self.feature_columns]
            .iloc[max(0, start) : end]
            .to_numpy(dtype=np.float32)
        )
        n_rows, n_feats = block.shape[0], block.shape[1]
        pad_len = self.window_size - n_rows
        if pad_len > 0:
            if n_rows > 0:
                # repeat the first real row
                pad_block = np.repeat(block[0:1, :], pad_len, axis=0)
            else:
                # no data yet – pad with zeros
                pad_block = np.zeros((pad_len, n_feats), dtype=np.float32)
            block = np.concatenate([pad_block, block], axis=0)
        pos_col = np.full((self.window_size, 1), self._position, dtype=np.float32)
        return np.concatenate([block, pos_col], axis=1)
