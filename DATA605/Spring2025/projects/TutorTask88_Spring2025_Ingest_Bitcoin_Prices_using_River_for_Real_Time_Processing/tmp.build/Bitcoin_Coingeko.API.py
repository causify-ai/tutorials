"""
Streams Bitcoin OHLC data and incrementally trains River regression models for real-time forecasting.

1. Code is based on DATA605 Spring 2025 project guidelines.
2. Ensure code passes linter (e.g., flake8 or pylint) before committing.
3. See detailed notebook explanation in: `gradeapi.pdf`.

File naming follows the standard format:
- For a River-based streaming simulation, the file is named `template.API.py`.

Reference coding guide:
https://github.com/causify-ai/helpers/blob/master/docs/coding/all.coding_style.how_to_guide.md
"""

import logging
from typing import List, Dict
from collections import deque

from river import linear_model, tree, preprocessing, metrics

from bitcoin_forecast_utils import (
    get_coin_ohlc,
    build_rolling_features
)

_LOG = logging.getLogger(__name__)


class Template:
    """
    A class that simulates a streaming environment to test River models using Bitcoin OHLC data.
    """

    def __init__(self) -> None:
        """
        Initializes OHLC data, model candidates, metrics, and a rolling window.
        """
        self.ohlc_df = get_coin_ohlc(days=1)
        self.close_prices = self.ohlc_df["close"]
        self.volatility = self.ohlc_df["high"] - self.ohlc_df["low"]
        self.rolling_prices = deque(maxlen=5)

        self.lr_model = linear_model.LinearRegression()
        self.tree_model = tree.HoeffdingTreeRegressor()
        self.pipe_model = preprocessing.StandardScaler() | linear_model.LinearRegression()

        self.mae_lr = metrics.MAE()
        self.mae_tree = metrics.MAE()
        self.mae_pipe = metrics.MAE()

        self.actual_log: List[float] = []
        self.lr_log: List[float] = []
        self.tree_log: List[float] = []
        self.pipe_log: List[float] = []
        self.vol_log: List[float] = []

    def method1(self, steps: int = 30) -> None:
        """
        Streams price data and performs real-time prediction, learning, and MAE tracking.

        :param steps: Number of time steps to simulate.
        """
        for step, price in enumerate(self.close_prices.head(steps)):
            self.rolling_prices.append(price)

            if len(self.rolling_prices) == self.rolling_prices.maxlen:
                features = build_rolling_features(self.rolling_prices)

                pred_lr = self.lr_model.predict_one(features)
                pred_tree = self.tree_model.predict_one(features)
                pred_pipe = self.pipe_model.predict_one(features)

                self.lr_model.learn_one(features, price)
                self.tree_model.learn_one(features, price)
                self.pipe_model.learn_one(features, price)

                self.mae_lr.update(price, pred_lr)
                self.mae_tree.update(price, pred_tree)
                self.mae_pipe.update(price, pred_pipe)

                self.actual_log.append(price)
                self.lr_log.append(pred_lr)
                self.tree_log.append(pred_tree)
                self.pipe_log.append(pred_pipe)
                self.vol_log.append(self.volatility.iloc[step])

                print(
                    f"Step {step+1}: Actual = {price:.2f} | "
                    f"LR = {pred_lr:.2f} | Tree = {pred_tree:.2f} | "
                    f"Pipe = {pred_pipe:.2f} | Vol = {self.vol_log[-1]:.2f}"
                )

        _LOG.info("Final MAE - LR: %.4f, Tree: %.4f, Pipeline: %.4f",
                  self.mae_lr.get(), self.mae_tree.get(), self.mae_pipe.get())

        print("\nFinal MAEs:")
        print(f"Linear Regression: {self.mae_lr.get():.4f}")
        print(f"Hoeffding Tree:    {self.mae_tree.get():.4f}")
        print(f"Pipeline (Scaler + LR): {self.mae_pipe.get():.4f}")

        print("\nModel Weights (Pipeline):")
        print(self.pipe_model[-1].weights)


def template_function(arg1: int) -> None:
    """
    Placeholder function for demonstration purposes.

    :param arg1: An integer argument (unused here).
    """
    print(f"This is a placeholder function. Received arg1 = {arg1}")


if __name__ == "__main__":
    Template().method1()
