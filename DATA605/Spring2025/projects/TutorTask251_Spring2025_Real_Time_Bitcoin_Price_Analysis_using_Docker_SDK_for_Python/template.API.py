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

# Following is a useful library for typehinting.
# For typehints like list, dict, etc. you can use the following:
## def func(arg1:List[int]) -> List[int]:
# For more info check: https://docs.python.org/3/library/typing.html
from typing import List

import pandas as pd
import numpy as np
import requests

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
    Brief imperative description of what the class does in one line, if needed.
    """

    def __init__(self):
        pass

    def method1(self, arg1: int) -> None:
        """
        Brief imperative description of what the method does in one line.

        You can elaborate more in the method docstring in this section, for
        e.g. explaining the formula/algorithm. Every method/function should
        have a docstring, typehints and include the parameters and return as
        follows:

        :param arg1: description of arg1
        :return: description of return
        """
        # Code bloks go here.
        # Make sure to include comments to explain what the code is doing.
        # No empty lines between code blocks.

    def fetch_histominute(self, fsym: str, tsym: str, limit: int = 60) -> pd.DataFrame:
        """
        Fetch historical minute-level data from CryptoCompare API.

        :param fsym: Base cryptocurrency symbol (e.g., 'BTC')
        :param tsym: Quote currency symbol (e.g., 'USD')
        :param limit: Number of minutes of data to retrieve (default 60)
        :return: Pandas DataFrame with historical minute data.
        """
        url = 'https://min-api.cryptocompare.com/data/v2/histominute'
        params = {'fsym': fsym, 'tsym': tsym, 'limit': limit}
        _LOG.info("Fetching historical minute data for %s/%s", fsym, tsym)
        response = requests.get(url, params=params)
        response.raise_for_status()
        json_data = response.json()
        data = json_data['Data']['Data']
        df = pd.DataFrame(data)
        return df


def template_function(arg1: int) -> None:
    """
    Brief imperative description of what the function does in one line.

    You can elaborate more in the function docstring in this section, for e.g.
    explaining the formula/algorithm. Every function should have a docstring,
    typehints and include the parameters and return as follows:

    :param arg1: description of arg1
    :return: description of return
    """
    # Code bloks go here.
    # Make sure to include comments to explain what the code is doing.
    # No empty lines between code blocks.
    pass


if __name__ == "__main__":
    # Example usage of the API call
    template = Template()
    df = template.fetch_histominute('BTC', 'USD', 60)
    _LOG.info("Retrieved %d records", len(df))
    print(df.head())
