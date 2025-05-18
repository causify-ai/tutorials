# stablebaseline3_utils.py

import requests
import pandas as pd
import numpy as np
import gymnasium as gym
from gymnasium import spaces

# ----------- API Functions -----------

def fetch_price_now(vs_currency="usd"):
    """Get current Bitcoin price from CoinGecko"""
    url = f"https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies={vs_currency}"
    response = requests.get(url)
    return response.json()["bitcoin"][vs_currency]

def fetch_historical_prices(vs_currency="usd", days=30):
    """Fetch hourly BTC prices over the last `days` days (automatic interval)"""
    url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": vs_currency, "days": days}
    response = requests.get(url, params=params)
    prices = response.json()["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df = df.set_index("timestamp")
    return df

def normalize_prices(df):
    """Normalize prices to z-scores"""
    df = df.copy()
    df["norm_price"] = (df["price"] - df["price"].mean()) / df["price"].std()
    return df

# ----------- Custom Gymnasium Environment -----------

class BitcoinTradingEnv(gym.Env):
    metadata = {"render_modes": ["human"]}

    def __init__(self, price_series, window_size=10):
        super().__init__()
        self.price_series = price_series.reset_index(drop=True)
        self.window_size = window_size
        self.initial_balance = 1000

        # Define observation and action space
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(window_size,),
            dtype=np.float32
        )
        self.action_space = spaces.Discrete(3)  # 0 = Hold, 1 = Buy, 2 = Sell

        self.reset()

    def _get_observation(self):
        obs = self.price_series["norm_price"].values[
            self.current_step - self.window_size : self.current_step
        ]
        return np.array(obs, dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_step = self.window_size
        self.balance = self.initial_balance
        self.shares_held = 0
        self.total_profit = 0.0
        return self._get_observation(), {}

    def step(self, action):
        current_price = self.price_series["price"].iloc[self.current_step]
        reward = 0

        if action == 1:  # Buy
            if self.balance > 0:
                self.shares_held += self.balance / current_price
                self.balance = 0

        elif action == 2:  # Sell
            if self.shares_held > 0:
                self.balance += self.shares_held * current_price
                reward = self.balance - self.initial_balance
                self.total_profit += reward
                self.shares_held = 0

        self.current_step += 1
        terminated = self.current_step >= len(self.price_series)
        truncated = False  # we don’t use time limits

        return self._get_observation(), reward, terminated, truncated, {}

    def render(self):
        print(f"Step {self.current_step} | Balance: ${self.balance:.2f} | Profit: ${self.total_profit:.2f}")
