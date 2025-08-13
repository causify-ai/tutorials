"""
Import as:

import tutorial_prophet.src.prophet_model as tpsrprmo
"""

import logging
from typing import Dict, Optional

import pandas as pd
import prophet
import sklearn

_LOG = logging.getLogger(__name__)


# #############################################################################
# ProphetForecastModel
# #############################################################################


class ProphetForecastModel:
    """
    Facebook Prophet wrapper.
    """

    def __init__(
        self, config: Dict, *, holidays: Optional[pd.DataFrame] = None
    ) -> None:
        """
        Initialize the Prophet model.

        :param config: Prophet hyperparameters
        :param holidays: data of holidays
        """
        self.config = config
        self.holidays = holidays
        self.model = prophet.Prophet(**config, holidays=holidays)
        self.fitted = False

    def fit(self, df: pd.DataFrame) -> None:
        """
        Fit the Prophet model on the given DataFrame.

        :param df: training data
        """
        for col in df.columns:
            if col not in ["ds", "y"]:
                _LOG.info("Adding regressor: %s", col)
                self.model.add_regressor(col)
        self.model.fit(df)
        self.fitted = True

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Predict future values using the fitted model.

        :param df: data of future timestamps
        :return: forecasted data
        """
        if not self.fitted:
            raise RuntimeError("Model must be fitted before prediction.")
        future = self.model.make_future_dataframe(periods=30)
        return self.model.predict(future)

    def evaluate(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Evaluate forecast against actuals.

        :param df: forecasted and actual data
        :return: forecast accuracy metrics
        """
        y_true = df["y"]
        y_pred = df["yhat"]
        return {
            "mae": sklearn.metrics.mean_absolute_error(y_true, y_pred),
            "rmse": sklearn.metrics.root_mean_squared_error(y_true, y_pred),
            "mape": (abs(y_true - y_pred) / y_true).mean() * 100,
        }

    def get_model(self) -> prophet.Prophet:
        """
        Get the internal Prophet object.
        """
        return self.model
