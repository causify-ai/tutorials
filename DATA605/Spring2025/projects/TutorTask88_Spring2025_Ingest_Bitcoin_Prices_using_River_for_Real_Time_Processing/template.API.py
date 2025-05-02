"""
A brief overview of what the script does in one line.

1. Make sure to include the citations here (code and research)
2. Make sure to run the linter on the script before committing changes.
    - Many changes would be pointed out by the linter to maintain consistency
      with coding style.
3. Provide here the reference to the documentation that explains the system in
   detail. (e.g., pycaret.API.md)

The name of this script should in the following format:
 - if the notebook is exploring `pycaret API`, then it is `pycaret.API.py`

 Follow the reference on coding style guide to write clean and readable code.
- https://github.com/causify-ai/helpers/blob/master/docs/coding/all.coding_style.how_to_guide.md
"""

# Comments should be imperative and have a period at the end.
# Your code should be well commented.
# Import libraries in this section.
# Avoid imports like import *, from ... import ..., from ... import *, etc.
import logging
import time

# Following is a useful library for typehinting.
# For typehints like list, dict, etc. you can use the following:
## def func(arg1:List[int]) -> List[int]:
# For more info check: https://docs.python.org/3/library/typing.html
from typing import List

import pandas as pd
import numpy as np
from river import linear_model, metrics, optim
from template_utils import get_bitcoin_price

_LOG = logging.getLogger(__name__)

# Prefer using logger over print statements.
# You can use logger in the following manner:
# ```
# _LOG.info("message") for logging level INFO
# _LOG.debug("message") for logging level DEBUG, etc.
# ```
# To add string formatting, use the following syntax:
# ```
# _LOG.info("message %s", "string") and so on.
# ```
_LOG = logging.getLogger(__name__)


# #############################################################################
# Template
# #############################################################################


class Template:
    """
    A class to stream Bitcoin prices and perform online learning using River.
    """

    def __init__(self):
        """
        Initializes the linear regression model and MAE metric.
        """
        self.model = linear_model.LinearRegression(optimizer=optim.SGD(0.01))
        self.metric = metrics.MAE()
        self.prev_price: Optional[float] = get_bitcoin_price()

    def method1(self, steps: int = 30) -> None:
        """
        Runs the online learning loop for a given number of steps.

        :param steps: Number of streaming data points to train on.
        :return: None
        """
        for step in range(steps):
            current_price = get_bitcoin_price()
            if current_price is None or self.prev_price is None:
                _LOG.warning("Skipping due to missing price data.")
                continue

            prediction = self.model.predict_one({'prev_price': self.prev_price})
            self.model.learn_one({'prev_price': self.prev_price}, current_price)
            self.metric.update(current_price, prediction)

            print(
                f"Step {step + 1}: Actual = {current_price} | "
                f"Predicted = {prediction:.2f} | MAE = {self.metric.get():.2f}"
            )

            self.prev_price = current_price
            time.sleep(10)


def template_function(arg1: int) -> None:
    """
    Placeholder function for demonstration purposes.

    :param arg1: An integer argument (unused here).
    :return: None
    """
    print(f"This is a placeholder function. Received arg1 = {arg1}")


if __name__ == "__main__":
    Template().method1()
