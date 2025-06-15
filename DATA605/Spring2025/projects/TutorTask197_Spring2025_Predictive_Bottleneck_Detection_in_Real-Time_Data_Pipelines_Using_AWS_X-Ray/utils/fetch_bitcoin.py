import requests
import time
from datetime import datetime, timedelta

def fetch_current_bitcoin_price():
    """
    Fetch the current Bitcoin price from CoinGecko API.
    """
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    response = requests.get(url)
    response.raise_for_status()  # Raise error for bad responses
    data = response.json()
    return data['bitcoin']['usd']

def get_unix_timestamp(dt):
    return int(dt.timestamp())

def get_bitcoin_price_history_hourly_chunks():
    """
    Fetches 365 days of hourly Bitcoin prices in 90-day chunks using
    CoinGecko's market_chart/range API, with rate limit handling.
    """
    base_url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range"
    vs_currency = "usd"
    all_prices = []

    end_time = datetime.now()
    start_time = end_time - timedelta(days=180)
    chunk_size = timedelta(days=90)

    current_start = start_time
    while current_start < end_time:
        current_end = min(current_start + chunk_size, end_time)

        from_ts = get_unix_timestamp(current_start)
        to_ts = get_unix_timestamp(current_end)

        params = {
            "vs_currency": vs_currency,
            "from": from_ts,
            "to": to_ts
        }

        success = False
        attempts = 0
        max_attempts = 2
        while not success and attempts < max_attempts:
            try:
                response = requests.get(base_url, params=params)
                response.raise_for_status()
                data = response.json()
                prices = data.get("prices", [])
                print(f"✅ Retrieved {len(prices)} prices from {current_start.date()} to {current_end.date()}")
                all_prices.extend(prices)
                success = True
            except requests.exceptions.HTTPError as e:
                print(f"❌ Failed ({attempts+1}/{max_attempts}) from {current_start.date()} to {current_end.date()}: {e}")
                if response.status_code == 429:
                    print("⏳ Waiting 10 seconds due to rate limit...")
                    time.sleep(10)
                else:
                    break  # for other errors, don't retry
            attempts += 1

        time.sleep(5)  # wait between chunks to avoid rate limits
        current_start = current_end

    return all_prices
