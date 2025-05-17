# utils.py

# -----------------------------------------------
# Imports
# -----------------------------------------------
import requests
import time
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Float, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# -----------------------------------------------
# SQLAlchemy Base Model
# -----------------------------------------------
Base = declarative_base()

class BitcoinPrice(Base):
    """
    Table to store Bitcoin price and timestamp
    """
    __tablename__ = 'bitcoin_prices'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    price = Column(Float)

# -----------------------------------------------
# Database Setup Functions
# -----------------------------------------------
def init_db(db_name="bitcoin_data.db"):
    """
    Create database and tables if they do not exist.
    """
    engine = create_engine(f"sqlite:///{db_name}")
    Base.metadata.create_all(engine)
    return engine

def get_session(engine):
    """
    Return a SQLAlchemy session for DB transactions.
    """
    Session = sessionmaker(bind=engine)
    return Session()

# -----------------------------------------------
# Real-Time Bitcoin Price (Single Value)
# -----------------------------------------------
def fetch_price():
    """
    Fetch current Bitcoin price in USD.
    """
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['bitcoin']['usd']
    else:
        raise Exception("API call failed with status code:", response.status_code)

def save_price(session, price):
    """
    Save real-time BTC price to the database.
    """
    entry = BitcoinPrice(price=price)
    session.add(entry)
    session.commit()
    print(f" Saved real-time price: ${price} at {entry.timestamp}")

# -----------------------------------------------
# Historical 30-Day Series Fetch
# -----------------------------------------------
def fetch_30day_price_series():
    """
    Fetches last 30 days of hourly Bitcoin prices using CoinGecko API.
    Returns a list of (timestamp, price) tuples.
    """
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=30"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Failed to fetch 30-day price series")

    data = response.json()
    prices = data['prices']  # List of [timestamp_ms, price]

    price_list = []
    for ts_ms, price in prices:
        ts = datetime.utcfromtimestamp(ts_ms / 1000.0)  # Convert ms to datetime
        price_list.append((ts, price))

    return price_list

# -----------------------------------------------
# Save Price Series to DB
# -----------------------------------------------
def save_price_series(session, price_list):
    """
    Save multiple timestamped BTC prices to the database.
    Skips duplicates.
    """
    count = 0
    for ts, price in price_list:
        existing = session.query(BitcoinPrice).filter(BitcoinPrice.timestamp == ts).first()
        if not existing:
            entry = BitcoinPrice(timestamp=ts, price=price)
            session.add(entry)
            count += 1
    session.commit()
    print(f" Inserted {count} new records from price series.")

# -----------------------------------------------
# Real-Time Data for 5 Minutes (Interval Sampling)
# -----------------------------------------------
def fetch_realtime_5min_series(interval_seconds=10):
    """
    Fetch and return Bitcoin prices every `interval_seconds` over the next 5 minutes.
    Returns a list of (timestamp, price).
    """
    price_list = []
    print(" Capturing real-time data for 5 minutes...")

    for i in range(int(300 / interval_seconds)):
        try:
            price = fetch_price()
            ts = datetime.utcnow()
            price_list.append((ts, price))
            print(f" {ts} → ${price}")
        except Exception as e:
            print(" Error fetching:", e)

        time.sleep(interval_seconds)

    return price_list

def load_data_from_db(db_name="bitcoin_data.db"):
    """
    Reloads Bitcoin data from SQLite after live ingestion.
    """
    engine = create_engine(f"sqlite:///{db_name}")
    df = pd.read_sql("SELECT * FROM bitcoin_prices", con=engine)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    df.sort_index(inplace=True)
    df.drop_duplicates(inplace=True)
    return df
