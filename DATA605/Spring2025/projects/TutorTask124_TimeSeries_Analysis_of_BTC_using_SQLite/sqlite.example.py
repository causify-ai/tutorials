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

import logging

from typing import List

import logging
import pandas as pd
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

API_KEY = # TO BE FILLED
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

## Open Price Moving Average - Data Range
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

# Volume
plt.figure(figsize=(15,5), dpi=100)
sns.lineplot(data=data, x='date', y='volume')
plt.title("BTC Opening price across time.")
plt.grid(True)
plt.xlabel("Date")
plt.ylabel("Volume")
plt.show(block=False)

## Volume Moving Average
query = '''SELECT
    date,
    volume,
    ROUND(AVG(volume) OVER (
        ORDER BY date
        ROWS BETWEEN 1 PRECEDING AND CURRENT ROW
    ), 2) AS ma_2d_vol, --Adding 2 Day Moving Average

    ROUND(AVG(volume) OVER (
        ORDER BY date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ), 2) AS ma_30d_vol, --Adding 30 Day Moving Average

    ROUND(AVG(volume) OVER (
        ORDER BY date
        ROWS BETWEEN 119 PRECEDING AND CURRENT ROW
    ), 2) AS ma_120d_vol --Adding 120 Day Moving Average
FROM btc_daily_stats
ORDER BY date;
'''
dataMA = sqlite_utils.fetchDB(query=query, db="./btcDaily.db")
dataMA['date'] = pd.to_datetime(dataMA['date'], format=DATEFMT)

plt.figure(figsize=(15,5), dpi=100)
sns.lineplot(data=dataMA, x='date', y='volume', label='Open Price', color='royalblue')
sns.lineplot(data=dataMA, x='date', y='ma_2d_vol', label='2day MA Volume', color='tomato')
sns.lineplot(data=dataMA, x='date', y='ma_30d_vol', label='30day MA Volume', color='orange')
sns.lineplot(data=dataMA, x='date', y='ma_120d_vol', label='120day MA Volume', color='forestgreen')

sns.scatterplot(x=[dataMA.iloc[-1]['date']], y=[dataMA.iloc[-1]['volume']], s=500, marker='*', color='red', label='Current BTC Volume')
plt.grid(True)
plt.xlabel("Date")
plt.ylabel("Volume")

plt.title("BTC Volume across time.")
plt.show(block=False)

## Volume Moving Average - Data Range
dateStart, dateEnd = '2024-12-24-00-00-00', '2025-04-15-00-00-00'

query = f'''SELECT
    date,
    volume,
    ROUND(AVG(volume) OVER (
        ORDER BY date
        ROWS BETWEEN 1 PRECEDING AND CURRENT ROW
    ), 2) AS ma_2d_vol,

    ROUND(AVG(volume) OVER (
        ORDER BY date
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ), 2) AS ma_30d_vol,

    ROUND(AVG(volume) OVER (
        ORDER BY date
        ROWS BETWEEN 119 PRECEDING AND CURRENT ROW
    ), 2) AS ma_120d_vol
FROM btc_daily_stats
WHERE date BETWEEN '{dateStart}' AND '{dateEnd}' --Adding Date Range
ORDER BY date;
'''

dataMA = sqlite_utils.fetchDB(query=query, db="./btcDaily.db")
dataMA['date'] = pd.to_datetime(dataMA['date'], format=DATEFMT)
dataMA.tail()

plt.figure(figsize=(15,5), dpi=100)
sns.lineplot(data=dataMA, x='date', y='volume', label='Open Price', color='royalblue')
sns.lineplot(data=dataMA, x='date', y='ma_2d_vol', label='2day MA Open Price', color='tomato')
sns.lineplot(data=dataMA, x='date', y='ma_30d_vol', label='30day MA Open Price', color='orange')
sns.lineplot(data=dataMA, x='date', y='ma_120d_vol', label='120day MA Open Price', color='forestgreen')

sns.scatterplot(x=[dataMA.iloc[-1]['date']], y=[dataMA.iloc[-1]['volume']], s=500, marker='*', color='red', label='Current BTC Volume')
plt.grid(True)
plt.xlabel("Date")
plt.ylabel("Volume")

plt.title(f"BTC Volume from {dateStart[:10]} to {dateEnd[:10]}")
plt.show(block = False)

# Candle stick
dateStart, dateEnd = '2024-08-24-00-00-00', '2025-04-15-00-00-00'
query = f"SELECT * FROM btc_daily_stats WHERE date BETWEEN '{dateStart}' AND '{dateEnd}' --Adding Date Range"
dataCS = sqlite_utils.fetchDB(query=query, db="./btcDaily.db")
dataCS['date'] = pd.to_datetime(dataCS['date'], format=DATEFMT)
dataCS['SMA'] = dataCS.open.rolling(window=20).mean()
dataCS['stddev'] = dataCS.open.rolling(window=20).std()
dataCS['upper'] = dataCS.SMA + 2 * dataCS.stddev
dataCS['lower'] = dataCS.SMA - 2 * dataCS.stddev
dataCS.set_index('date', inplace=True)

tcdf = dataCS[['lower','upper','SMA']]

apd = mpf.make_addplot(tcdf)
mpf.plot(dataCS, figratio=(15,5), type='candle', addplot=apd, volume=False, style='yahoo',title=f'BTC Price Chart from {dateStart[:10]} to {dateEnd[:10]}')

# Rate of Change
dateStart, dateEnd = '2024-12-01-00-00-00', '2025-04-15-00-00-00'

query = f'''SELECT
    date,
    open,
    -- 1-day Rate of Change
    ROUND(((open - LAG(open, 1) OVER (ORDER BY date)) / LAG(open, 1) OVER (ORDER BY date)) * 100, 2) AS roc_1d,

    -- 30-day Rate of Change
    ROUND(((open - LAG(open, 30) OVER (ORDER BY date)) / LAG(open, 30) OVER (ORDER BY date)) * 100, 2) AS roc_30d,

    -- 120-day Rate of Change
    ROUND(((open - LAG(open, 120) OVER (ORDER BY date)) / LAG(open, 120) OVER (ORDER BY date)) * 100, 2) AS roc_120d

FROM btc_daily_stats
WHERE date BETWEEN '{dateStart}' AND '{dateEnd}'
ORDER BY date'''

dataRC = sqlite_utils.fetchDB(query=query, db="./btcDaily.db")
dataRC['date'] = pd.to_datetime(dataRC['date'], format=DATEFMT)

f, ax = plt.subplots(nrows=3,ncols=1, figsize=(20,8), sharex=True)

colors = ['tomato' if val <=0 else 'limegreen' for val in dataRC['roc_1d']]
ax[0].bar(x=dataRC['date'], height=dataRC['roc_1d'], color=colors)
ax[0].set_title("1day percentage change across time.")
ax[0].set_ylabel("% Change")

colors = ['tomato' if val <=0 else 'limegreen' for val in dataRC['roc_30d']]
ax[1].bar(x=dataRC['date'], height=dataRC['roc_30d'], color=colors)
ax[1].set_title("30day percentage change across time.")
ax[1].set_ylabel("% Change")

colors = ['tomato' if val <=0 else 'limegreen' for val in dataRC['roc_120d']]
ax[2].bar(x=dataRC['date'], height=dataRC['roc_120d'], color=colors)
ax[2].set_title("120day percentage change across time.")
ax[2].set_xlabel("Time")
ax[2].set_ylabel("% Change")

plt.show(block=False)

# Volatility
dateStart, dateEnd = '2024-04-01-00-00-00', '2025-04-15-00-00-00'

query = f'''SELECT
    date,
    open,
    -- 1-day Rate of Change
    ROUND(((open - LAG(open, 1) OVER (ORDER BY date)) / LAG(open, 1) OVER (ORDER BY date)) * 100, 2) AS roc_1d,

    -- 30-day Rate of Change
    ROUND(((open - LAG(open, 30) OVER (ORDER BY date)) / LAG(open, 30) OVER (ORDER BY date)) * 100, 2) AS roc_30d,

    -- 120-day Rate of Change
    ROUND(((open - LAG(open, 120) OVER (ORDER BY date)) / LAG(open, 120) OVER (ORDER BY date)) * 100, 2) AS roc_120d

FROM btc_daily_stats
WHERE date BETWEEN '{dateStart}' AND '{dateEnd}'
ORDER BY date'''

dataV = sqlite_utils.fetchDB(query=query, db="./btcDaily.db")
dataV['date'] = pd.to_datetime(dataV['date'], format=DATEFMT)
dataV['daily_return'] = dataV['open'].pct_change()
dataV['volatility_2d'] = dataV['daily_return'].rolling(window=5).std()
dataV['volatility_30d'] = dataV['daily_return'].rolling(window=30).std()
dataV['volatility_120d'] = dataV['daily_return'].rolling(window=120).std()

plt.figure(figsize=(15,5), dpi=150)
sns.lineplot(data=dataV, x='date', y='volatility_2d', label='2D Volatility', color='royalblue')
sns.lineplot(data=dataV, x='date', y='volatility_30d', label='30D Volatility', color='tomato')
sns.lineplot(data=dataV, x='date', y='volatility_120d', label='120D Volatility', color='forestgreen')
plt.title("5, 30, 120 Day Volatility Across Time.")
plt.xlabel("Date")
plt.ylabel("Volatility")
plt.show(block=False)

# Histogram of Daily Records

dateStart, dateEnd = '2024-04-01-00-00-00', '2025-04-15-00-00-00'

query = f'''SELECT
    date,
    open,
    -- 1-day Rate of Change
    ROUND(((open - LAG(open, 1) OVER (ORDER BY date)) / LAG(open, 1) OVER (ORDER BY date)) * 100, 2) AS roc_1d,

    -- 30-day Rate of Change
    ROUND(((open - LAG(open, 30) OVER (ORDER BY date)) / LAG(open, 30) OVER (ORDER BY date)) * 100, 2) AS roc_30d,

    -- 120-day Rate of Change
    ROUND(((open - LAG(open, 120) OVER (ORDER BY date)) / LAG(open, 120) OVER (ORDER BY date)) * 100, 2) AS roc_120d

FROM btc_daily_stats
WHERE date BETWEEN '{dateStart}' AND '{dateEnd}'
ORDER BY date'''

dataV = sqlite_utils.fetchDB(query=query, db="./btcDaily.db")
dataV['date'] = pd.to_datetime(dataV['date'], format=DATEFMT)
dataV['daily_return'] = dataV['open'].pct_change()
dataV['volatility_2d'] = dataV['daily_return'].rolling(window=5).std()
dataV['volatility_30d'] = dataV['daily_return'].rolling(window=30).std()
dataV['volatility_120d'] = dataV['daily_return'].rolling(window=120).std()

plt.figure(figsize=(15,5), dpi=100)
sns.histplot(data=dataV['daily_return'].dropna(), color='royalblue', bins=100, stat='probability',edgecolor='black')
plt.axvline(x = dataV['daily_return'].dropna().mean(), color ='red', linestyle ="--",linewidth=1.5, label = 'Mean')
plt.axvline(x = dataV['daily_return'].dropna().median(), color ='orange', linestyle ="--",linewidth=1.5, label = 'Median')
plt.legend()
plt.title("Histogram of Daily Records of BTC")
plt.xlabel("Daily Returns")
plt.ylabel("Probability")
plt.show(block = False)

plt.show()
