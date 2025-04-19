"""
template_utils.py

This file contains utility functions that support the tutorial notebooks.

- Notebooks should call these functions instead of writing raw logic inline.
- This helps keep the notebooks clean, modular, and easier to debug.
- Students should implement functions here for data preprocessing,
  model setup, evaluation, or any reusable logic.
"""

import logging
from requests import Request, Session
import pandas as pd
import sqlite3
import mplfinance as mpf
import yfinance as yf

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# fetchHistoricalBTC: Function to fetch historical BTC prices from Yahoo Finance.
# -----------------------------------------------------------------------------

def fetchHistoricalBTC(ticker, period, interval):
    """
    Function to fetch historical BTC prices from Yahoo Finance.

    Fetches historical stock data for BTC using the yfinance Python library. 
    The function retrieves data such as open, high, low, close, volume, and adjusted close 
    for a specified date range and interval.

    :param ticker (str): Ticker of stock.
    :param period (str): Period of data for which to fetch the data of.
    :param interval (str): Frequency of data to be fetched.
    :return: Pandas DataFrame containing the data.
    """
    data = yf.download(ticker, period=period, progress=False, interval=interval).reset_index()
    data.columns = ['date', 'close', 'high', 'low', 'open', 'volume']
    data['date'] = data['date'].dt.strftime(DATEFMT)

    return data

# -----------------------------------------------------------------------------
# storeData: Function to store historical data into a SQLite Database.
# -----------------------------------------------------------------------------

def storeData(data, db):
    """
    Function to store historical data into a SQLite Database.

    Pushes the provided data into a database(to be provided too), if the database exists,
    otherwise creates a database for the same.

    :param data: Data to be stored.
    :param db: Path to the SQLite database file. Database where data is meant to be pushed.
    :return: None.
    """
    conn = sqlite3.connect(db)
    data.to_sql('btc_daily_stats', conn, if_exists='replace', index=False)
    conn.close()

    return None

# -----------------------------------------------------------------------------
# fetchDB: Function to execute a user query on a provided DataBase in SQLite.
# -----------------------------------------------------------------------------

def fetchDB(query, db):
    """
    Function to execute a user query on a provided DataBase in SQLite.

    :param query (str): SQL Query to be executed.
    :param db: Path to the SQLite database file. SQLite database on which query is to be executed.
    :return: Pandas Dataframe of the data executed using SQLite from the database.
    
    """
    conn = sqlite3.connect(db)
    return pd.read_sql_query(query, conn)

# -----------------------------------------------------------------------------
# liveBTC: Fetches live Bitcoin price data from CoinMarketCap using a provided API key and URL.
# -----------------------------------------------------------------------------

def liveBTC(url,API_KEY):
    """
    Fetches live Bitcoin price data from CoinMarketCap using a provided API key and URL.

    :param url (str): The CoinMarketCap API endpoint.
    :param api_key (str): The API key for authenticating the request.

    :return dict: A dictionary containing the current timestamp, open price, volume, 
          and additional data such as volume change.
    """
    params = {'symbol': 'BTC','convert': 'USD'}
    
    headers = {'Accepts': 'application/json','X-CMC_PRO_API_KEY': API_KEY}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        print("ERROR CODE: ",response.status_code, " : ", response.text)
        return None, None
    data = response.json()
    
    btc = data['data']['BTC'][0]['quote']['USD']
    last_updated = data['data']['BTC'][0]['last_updated']
    
    btc_data_prime = {'date': pd.Timestamp(last_updated).strftime(DATEFMT), 'open': btc['price'], 'volume': btc['volume_24h']}

    return btc_data_prime, btc 

# -----------------------------------------------------------------------------
# addDatapoint: Function to insert live Bitcoin price data into a SQLite database.
# -----------------------------------------------------------------------------

def addDatapoint(liveData, db):
    """
    Function to insert live Bitcoin price data into a SQLite database.
    
    :param data (dict): A dictionary containing:
    - 'timestamp' (str or datetime): The current time.
    - 'open_price' (float): The opening price of BTC.
    - 'volume' (float): The trading volume.
    
    :param db (str): Path to the SQLite database file.
    
    :return None: The function inserts the data and does not return a value
    """
    date, liveOpen, volume = liveData['date'],liveData['open'],liveData['volume']
    query = f'''INSERT INTO btc_daily_stats (date, open, volume) VALUES (STRFTIME({DATEFMT},{date}), {liveOpen}, {volume})'''
    query = f'''INSERT INTO btc_daily_stats (date, open, volume) VALUES (?,?,?)'''
    
    cursor = conn.cursor()
    cursor.execute(query, (date, liveOpen, volume))
    conn.commit()
    return cursor.lastrowid
    