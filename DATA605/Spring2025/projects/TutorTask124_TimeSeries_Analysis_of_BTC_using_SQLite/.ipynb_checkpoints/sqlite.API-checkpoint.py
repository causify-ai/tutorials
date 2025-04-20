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

import logging
from requests import Request, Session
import pandas as pd
import sqlite3
import mplfinance as mpf
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite_utils

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
# Bitcoin API Setup using SQLite Script
# #############################################################################

API_KEY = 'bdbd5008-53de-4bf9-b9b8-c1edb2c6afb0'
headers = {'X-CMC_PRO_API_KEY': API_KEY,'Accept': 'application/json'}
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
params = {'limit': 1,'convert': 'USD'}

DATEFMT = "%Y-%m-%d-%H-%M-%S"

# Load Data
data = sqlite_utils.fetchHistoricalBTC(ticker="BTC-USD", period='15y', interval='1d')

# Storing Data into SQLite
sqlite_utils.storeData(data=data, db="./btcDaily.db")

# Query Data from SQLite
query = "SELECT * FROM btc_daily_stats"
data = sqlite_utils.fetchDB(query=query, db="./btcDaily.db")

# Live BTC Price
url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
API_KEY = 'bdbd5008-53de-4bf9-b9b8-c1edb2c6afb0'
btcLiveData, btcAuxData = sqlite_utils.liveBTC(url=url, API_KEY=API_KEY)

# Inserting Live Data into SQLite
sqlite_utils.addDatapoint(liveData=btcLiveData, db="./btcDaily.db")

# #############################################################################
# Bitcoin Analysis using SQLite Script
# #############################################################################
# 

query = "SELECT * FROM btc_daily_stats"
data = sqlite_utils.fetchDB(query=query, db="./btcDaily.db")
data['date'] = pd.to_datetime(data['date'], format=DATEFMT)

# Bitcoin Open Price
plt.figure(figsize=(15,5), dpi=100)
sns.lineplot(data=data, x='date', y='open')
sns.scatterplot(x=[data.iloc[-1]['date']], y=[data.iloc[-1]['open']], s=500, marker='*', color='red', label='Current BTC Price') 
plt.grid(True)
plt.xlabel("Date")
plt.ylabel("Opening Price")
plt.title("BTC Opening price across time.")
plt.show(block=False)

## Moving Average
query = '''SELECT 
    date,
    open,
    ROUND(AVG(open) OVER (
        ORDER BY date 
        ROWS BETWEEN 1 PRECEDING AND CURRENT ROW
    ), 2) AS ma_2d_open, --Adding 2 Day Moving Average
    
    ROUND(AVG(open) OVER (
        ORDER BY date 
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ), 2) AS ma_30d_open, --Adding 30 Day Moving Average
    
    ROUND(AVG(open) OVER (
        ORDER BY date 
        ROWS BETWEEN 119 PRECEDING AND CURRENT ROW
    ), 2) AS ma_120d_open --Adding 120 Day Moving Average
FROM btc_daily_stats
ORDER BY date;
'''
dataMA = sqlite_utils.fetchDB(query=query, db="./btcDaily.db")
dataMA['date'] = pd.to_datetime(dataMA['date'], format=DATEFMT)

plt.figure(figsize=(15,5), dpi=100)
sns.lineplot(data=dataMA, x='date', y='open', label='Open Price', color='royalblue')
sns.lineplot(data=dataMA, x='date', y='ma_2d_open', label='2day MA Open Price', color='tomato')
sns.lineplot(data=dataMA, x='date', y='ma_30d_open', label='30day MA Open Price', color='orange')
sns.lineplot(data=dataMA, x='date', y='ma_120d_open', label='120day MA Open Price', color='forestgreen')

sns.scatterplot(x=[dataMA.iloc[-1]['date']], y=[dataMA.iloc[-1]['open']], s=500, marker='*', color='red', label='Current BTC Price') 
plt.grid(True)
plt.xlabel("Date")
plt.ylabel("Opening Price")
plt.title("BTC Opening price across time.")
plt.show(block=False)

## Moving Average - Data Range
dateStart, dateEnd = '2024-12-24-00-00-00', '2025-04-15-00-00-00'

query = f'''SELECT 
    date,
    open,
    ROUND(AVG(open) OVER (
        ORDER BY date 
        ROWS BETWEEN 1 PRECEDING AND CURRENT ROW
    ), 2) AS ma_2d_open,
    
    ROUND(AVG(open) OVER (
        ORDER BY date 
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ), 2) AS ma_30d_open,
    
    ROUND(AVG(open) OVER (
        ORDER BY date 
        ROWS BETWEEN 119 PRECEDING AND CURRENT ROW
    ), 2) AS ma_120d_open
FROM btc_daily_stats
WHERE date BETWEEN '{dateStart}' AND '{dateEnd}' --Adding Date Range
ORDER BY date;
'''

dataMA = sqlite_utils.fetchDB(query=query, db="./btcDaily.db")
dataMA['date'] = pd.to_datetime(dataMA['date'], format=DATEFMT)

plt.figure(figsize=(15,5), dpi=100)
sns.lineplot(data=dataMA, x='date', y='open', label='Open Price', color='royalblue')
sns.lineplot(data=dataMA, x='date', y='ma_2d_open', label='2day MA Open Price', color='tomato')
sns.lineplot(data=dataMA, x='date', y='ma_30d_open', label='30day MA Open Price', color='orange')
sns.lineplot(data=dataMA, x='date', y='ma_120d_open', label='120day MA Open Price', color='forestgreen')

sns.scatterplot(x=[dataMA.iloc[-1]['date']], y=[dataMA.iloc[-1]['open']], s=400, marker='*', color='red', label='Current BTC Price') 
plt.grid(True)
plt.xlabel("Data")
plt.ylabel("Opening Price")

plt.title(f"BTC Opening price from {dateStart[:10]} to {dateEnd[:10]}")
plt.show(block=False)


plt.show()
