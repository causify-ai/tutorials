"""
Fetches historical and live Bitcoin price data using Yahoo Finance and CoinMarketCap APIs,
and manages storage and retrieval via a local SQLite database using helper utilities.

1. Citations:
   - Historical Data Source: Yahoo Finance via `yfinance` (https://github.com/ranaroussi/yfinance)
   - Live Price Source: CoinMarketCap API (https://coinmarketcap.com/api/)
   - Data Persistence: SQLite via `sqlite3` and custom `sqlite_utils.py`
   - Visualization tools: `matplotlib`, `seaborn`, and `mplfinance`

2. Make sure to run the linter (e.g., `ruff`, `black`, or `flake8`) on the script before committing changes.
   - Example: `ruff check api_btc_script.py --fix`

3. References:
   - Custom utility documentation: `sqlite_utils.py`
   - System design and data flow: `docs/system/bitcoin_analysis_system.md`
   - CoinMarketCap API documentation: https://coinmarketcap.com/api/documentation/v1/

Script Naming Convention:
 - If this script is responsible for integrating API data into SQLite for BTC analysis:
   `bitcoin.api_ingestion.py`

Coding Style Guide Reference:
 - https://github.com/causify-ai/helpers/blob/master/docs/coding/all.coding_style.how_to_guide.md
"""



import logging

# Import standard and third-party libraries for logging, HTTP requests, data handling, visualization, and database operations.
import logging
from requests import Request, Session
import pandas as pd
import sqlite3
import mplfinance as mpf
import yfinance as yf
import matplotlib.pyplot as plt
%matplotlib inline
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
# API Script
# #############################################################################


# Set your CoinMarketCap API key.
API_KEY = # TO BE FILLED

# Define headers for API authentication and response format.
headers = {'X-CMC_PRO_API_KEY': API_KEY,'Accept': 'application/json'}

# Define the endpoint URL for fetching latest cryptocurrency listings.
url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

# Set request parameters: limit results and specify currency conversion.
params = {'limit': 1,'convert': 'USD'}

# Set the date format string for consistent datetime parsing.
DATEFMT = "%Y-%m-%d-%H-%M-%S"

# Fetch 15 years of daily BTC-USD historical data using a custom sqlite_utils function.
data = sqlite_utils.fetchHistoricalBTC(ticker="BTC-USD", period='15y', interval='1d')


# Store the DataFrame into a local SQLite database file named 'btcDaily.db'.
sqlite_utils.storeData(data=data, db="./btcDaily.db")

# Define SQL query to select all records from the btc_daily_stats table.
query = "SELECT * FROM btc_daily_stats"

# Fetch the data from the database.
data = sqlite_utils.fetchDB(query=query, db="./btcDaily.db")


# Define the endpoint for live Bitcoin quotes.
url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'

# Fetch live Bitcoin data and additional statistics using a custom utility.
btcLiveData, btcAuxData = sqlite_utils.liveBTC(url=url, API_KEY=API_KEY)

# Add the latest live data point to the local SQLite database.
sqlite_utils.addDatapoint(liveData=btcLiveData, db="./btcDaily.db")
