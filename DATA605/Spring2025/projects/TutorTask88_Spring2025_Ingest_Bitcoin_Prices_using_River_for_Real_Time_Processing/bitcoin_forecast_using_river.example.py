"""
bitcoin_forecast_using_river.example.py

Simulates a streaming Bitcoin forecasting loop using River with OHLC data.

References:
- River Documentation: https://riverml.xyz/latest/
- CoinGecko OHLC Endpoint: https://www.coingecko.com/en/api/documentation

Coding Style Guide: https://github.com/causify-ai/helpers/blob/master/docs/coding/all.coding_style.how_to_guide.md
"""

import logging
from collections import deque

import pandas as pd
from river import linear_model, metrics, preprocessing, tree

from bitcoin_forecast_utils import get_coin_ohlc, build_rolling_features, extract_ohlc_features

_LOG = logging.getLogger(__name__)


class BitcoinForecastExample:
    """
    Class to simulate streaming OHLC Bitcoin price forecasting using River.
    """

    def __init__(self):
        # Fetch OHLC data and initialize state
        self.ohlc_df = get_coin_ohlc(days=1)
        self.close_prices = self.ohlc_df['close']
        self.rolling_prices = deque(maxlen=5)

        # Initialize models
        self.lr_model = linear_model.LinearRegression()
        self.tree_model = tree.HoeffdingTreeRegressor()
        self.pipeline_model = preprocessing.StandardScaler() | linear_model.LinearRegression()

        # Initialize metrics
        self.lr_mae = metrics.MAE()
        self.tree_mae = metrics.MAE()
        self.pipe_mae = metrics.MAE()

        # Logs
        self.actual_log = []
        self.lr_log = []
        self.tree_log = []
        self.pipe_log = []
        self.vol_log = []

        # OHLC features
        self.ohlc_features_df = extract_ohlc_features(self.ohlc_df)

    def stream_forecast(self, steps: int = 30):
        """
        Simulate real-time streaming forecast using River models.

        :param steps: Number of steps to simulate (default is 30)
        """
        for step, price in enumerate(self.close_prices.head(steps)):
            self.rolling_prices.append(price)
            if len(self.rolling_prices) < self.rolling_prices.maxlen:
                continue

            features = build_rolling_features(self.rolling_prices)

            # Predictions
            lr_pred = self.lr_model.predict_one(features)
            tree_pred = self.tree_model.predict_one(features)
            pipe_pred = self.pipeline_model.predict_one(features)

            # Train models
            self.lr_model.learn_one(features, price)
            self.tree_model.learn_one(features, price)
            self.pipeline_model.learn_one(features, price)

            # Update metrics
            self.lr_mae.update(price, lr_pred)
            self.tree_mae.update(price, tree_pred)
            self.pipe_mae.update(price, pipe_pred)

            # Logging
            self.actual_log.append(price)
            self.lr_log.append(lr_pred)
            self.tree_log.append(tree_pred)
            self.pipe_log.append(pipe_pred)
            self.vol_log.append(features.get("volatility", None))

            print(
                f"Step {step + 1:2d} | "
                f"Actual: {price:8.2f} | "
                f"LR: {lr_pred:8.2f} | "
                f"Tree: {tree_pred:8.2f} | "
                f"Pipe: {pipe_pred:8.2f} | "
                f"Volatility: {features.get('volatility', 0):.4f}"
            )

        # Final MAE
        print("\nFinal MAE:")
        print(f"Linear Regression: {self.lr_mae.get():.4f}")
        print(f"Hoeffding Tree:     {self.tree_mae.get():.4f}")
        print(f"Pipeline Model:     {self.pipe_mae.get():.4f}")

        print("\nModel Weights (Pipeline):")
        print(dict(self.pipeline_model[-1].weights))


if __name__ == "__main__":
    forecast_sim = BitcoinForecastExample()
    forecast_sim.stream_forecast()
