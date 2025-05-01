"""
Custom environment for Bitcoin trading using TensorFlow Agents.

"""

import numpy as np
import pandas as pd
from typing import List, Optional
from pathlib import Path
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
        feature_columns: List[str] = None,
    ):
        """
        Initializes the Bitcoin trading environment.

        :param df: DataFrame containing the Bitcoin price data.
        :param window_size: Size of the observation window.
        :param fee: Transaction fee for buying/selling Bitcoin per trade (fraction of the trade amount).
        :param feature_columns: List of feature columns to be used in the observation space.
        """
        super().__init__()
        self._df = df
        self.window_size = window_size
        self._fee = fee
        # Internal State
        self._current_tick = None
        self._position = 0  #  0=flat, +1=long, -1=short
        # Specifiications
        self.feature_columns = feature_columns or [
            "Log_Returns",
            "Price_SMA_20",
            "Volume_SMA_20",
            "Volume",
        ]
        self.num_price_feats = len(feature_columns)
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
            0: Buy
            1: Sell
            2: Hold
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
            # Previous position
            prev_pos = self._position

            # Update the position based on the action taken
            if action == 2:
                self._position = +1
            elif action == 0:
                self._position = -1
            # action == 1: do nothing => position remains unchanged
            # Compute the reward using price log-returns
            price_t = self._df.loc[self._current_tick, "Close"]
            price_tp1 = self._df.loc[self._current_tick + 1, "Close"]
            log_ret = np.log(price_tp1 / price_t)
            trade_cost = abs(self._position - prev_pos) * self.fee
            reward = self._position * log_ret - trade_cost
            # Update the current tick
            self._current_tick += 1
            # Check if the episode is done
            if self._current_tick >= len(self._df) - 1:
                return ts.termination(self._get_observation(), reward)
            # Next Observation and transition
            return ts.transition(self._get_observation(), reward=reward, discount=1.0)

        def _get_observation(self) -> np.ndarray:
            # Slice the last window_size rows from the DataFrame
            start = self._current_tick - self.window_size + 1
            end = self._current_tick + 1
            block = self._df[self.feature_columns].iloc[start:end].values(np.float32)
            pos_col = np.full((self.window_size, 1), self._position, dtype=np.float32)
            return np.concatenate((block, pos_col), axis=1)
