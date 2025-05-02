# utils.py

import requests
from sqlalchemy import create_engine, Column, Float, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# ORM Base Class
Base = declarative_base()

# ORM Table: Bitcoin Prices
class BitcoinPrice(Base):
    __tablename__ = 'bitcoin_prices'
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    price = Column(Float)

# Initialize Database
def init_db(db_name="bitcoin_data.db"):
    engine = create_engine(f"sqlite:///{db_name}")
    Base.metadata.create_all(engine)
    return engine

# Create DB Session
def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()

# Fetch Bitcoin Price from CoinGecko
def fetch_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['bitcoin']['usd']
    else:
        raise Exception("API call failed")

# Save to Database
def save_price(session, price):
    entry = BitcoinPrice(price=price)
    session.add(entry)
    session.commit()
    print(f"✅ Saved BTC price ${price} at {entry.timestamp}")
