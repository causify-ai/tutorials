"""
utils.py

This file contains utility functions that support the tutorial notebooks.

function:
This file contains utility functions that support the tutorial notebooks.

Functions:

1. `fetch_bitcoin_prices`:
    Fetches historical Bitcoin price data from the CoinGecko API for a given date range and returns a list of (date, price) tuples.

2. `fetch_current_bitcoin_price`:
    Fetches the current real-time Bitcoin price and timestamp from the CoinGecko API.

3. `stream_prices`:
    Streams real-time Bitcoin price data for a specified duration and interval, then returns it as a PyArrow Table.

These utilities can be reused across notebooks for API interaction, data collection, and streaming demonstrations.
"""

import requests
import time
import pyarrow as pa
from datetime import datetime

def fetch_bitcoin_prices(start_date: str, end_date: str, api_key: str) -> list:
    """
    Fetch Bitcoin daily price data from the CoinGecko API within a specified date range.

    Args:
        start_date (str): Start date in 'YYYY-MM-DD' format.
        end_date (str): End date in 'YYYY-MM-DD' format.
        api_key (str): Your CoinGecko demo API key.

    Returns:
        list: A list of tuples containing (date, price) or an empty list if no data is found.
    """
    try:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError as e:
        print(f"Date format error: {e}")
        return []

    # Convert to UNIX timestamps
    from_timestamp = int(time.mktime(start_dt.timetuple()))
    to_timestamp = int(time.mktime(end_dt.timetuple()))

    # API endpoint and request setup
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range"
    params = {
        'vs_currency': 'usd',
        'from': from_timestamp,
        'to': to_timestamp
    }
    headers = {
        'x_cg_demo_api_key': api_key
    }

    # Make the API call
    response = requests.get(url, params=params, headers=headers)

    # Handle response
    if response.status_code == 200:
        data = response.json()
        prices = data.get('prices', [])

        return [
            (datetime.utcfromtimestamp(ts / 1000).strftime('%Y-%m-%d'), round(price, 2))
            for ts, price in prices
        ]
    else:
        print(f"API call failed with status code {response.status_code}")
        return []
    

def fetch_current_bitcoin_price(api_key: str):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        'ids': 'bitcoin',
        'vs_currencies': 'usd'
    }
    headers = {
        'x_cg_demo_api_key': api_key
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        price = data['bitcoin']['usd']
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        return timestamp, price
    else:
        print(f"[{datetime.utcnow()}] Failed to fetch: {response.status_code}")
        return None, None

def stream_prices(api_key: str, duration_sec: int = 60, interval_sec: int = 5):
    schema = pa.schema([
        ('timestamp', pa.string()),
        ('price_usd', pa.float64())
    ])
    
    batch_data = []

    print(f"Streaming for {duration_sec} seconds...")

    start_time = time.time()
    while (time.time() - start_time) < duration_sec:
        ts, price = fetch_current_bitcoin_price(api_key)
        if ts and price:
            batch_data.append((ts, price))
            print(f"{ts}: ${price}")
        time.sleep(interval_sec)

    return pa.Table.from_pylist(batch_data, schema=schema)