"""
Test suite for the BitcoinTradingEnv class.
"""

import sys
import os
import pytest
import numpy as np
import pandas as pd
from tf_agents.trajectories.time_step import StepType

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bitcoin_trading_env import BitcoinTradingEnv


@pytest.fixture
def simple_df() -> pd.DataFrame:
    """
    Creates a simple DataFrame with 6 rows and necessary columns for testing.
    """
    data = {
        "Log_Returns": [
            0.0,
            np.log(2 / 1),
            np.log(3 / 2),
            np.log(4 / 3),
            np.log(5 / 4),
            np.log(6 / 5),
        ],
        "Price_SMA_20": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
        "Volume_SMA_20": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0],
        "Volume": [10.0, 20.0, 30.0, 40.0, 50.0, 60.0],
        "Close": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
    }
    return pd.DataFrame(data)


def test_init_and_specs(simple_df: pd.DataFrame):
    """
    Test the initialization of the environment and its action/observation specs.
    """
    env = BitcoinTradingEnv(simple_df, window_size=3, fee=0.01)
    # Attributes
    assert env.window_size == 3
    assert pytest.approx(env.fee) == 0.01
    assert env.feature_columns == [
        "Log_Returns",
        "Price_SMA_20",
        "Volume_SMA_20",
        "Volume",
    ]
    assert env.num_price_feats == 4

    # Action spec
    a_spec = env.action_spec()
    assert a_spec.shape == ()
    assert a_spec.dtype == np.int32
    assert a_spec.minimum == 0
    assert a_spec.maximum == 2

    # Observation spec
    o_spec = env.observation_spec()
    assert o_spec.shape == (3, 5)
    assert o_spec.dtype == np.float32
    assert np.all(o_spec.minimum < -1e30)
    assert np.all(o_spec.maximum > 1e30)


def test_reset(simple_df: pd.DataFrame):
    env = BitcoinTradingEnv(simple_df, window_size=3)
    ts = env.reset()
    assert ts.step_type == StepType.FIRST
    obs = ts.observation
    assert isinstance(obs, np.ndarray)
    assert obs.shape == (3, 5)
    assert obs.dtype == np.float32
    # current_tick starts at window_size
    assert env._current_tick == 2
    # Position column zeros
    assert np.all(obs[:, -1] == 0.0)


def test_hold_action(simple_df: pd.DataFrame):
    env = BitcoinTradingEnv(simple_df, window_size=3, fee=0.0)
    env.reset()
    ts = env.step(1)  # Hold
    assert ts.step_type == StepType.MID
    assert ts.reward == 0.0
    assert env._current_tick == 3


def test_buy_and_short_actions(simple_df: pd.DataFrame):
    env = BitcoinTradingEnv(simple_df, window_size=3, fee=0.0)
    env.reset()
    # Buy then Short
    ts_buy = env.step(2)
    assert ts_buy.step_type == StepType.MID
    expected_buy = np.log(4 / 3)
    np.testing.assert_almost_equal(ts_buy.reward, expected_buy, decimal=6)
    # Tick moved to 4
    assert env._current_tick == 3

    ts_short = env.step(0)
    assert ts_short.step_type == StepType.MID
    expected_short = -np.log(5 / 4)
    np.testing.assert_almost_equal(ts_short.reward, expected_short, decimal=6)
    assert env._current_tick == 4


def test_termination_and_error(simple_df: pd.DataFrame):
    # Short DataFrame for early termination
    df_small = simple_df.iloc[:5]
    env = BitcoinTradingEnv(df_small, window_size=3)
    env.reset()
    # One step leads to termination
    ts_second_last = env.step(1)
    assert ts_second_last.step_type == StepType.MID
    ts_last = env.step(1)
    assert ts_last.step_type == StepType.LAST
    # Further steps error
    with pytest.raises(Exception):
        env.step(1)


def test_random_policy_run(simple_df: pd.DataFrame):
    env = BitcoinTradingEnv(simple_df, window_size=3)
    ts = env.reset()
    steps = 0
    while not ts.is_last() and steps < 10:
        ts = env.step(np.random.randint(0, 3))
        steps += 1
    assert ts.is_last()
