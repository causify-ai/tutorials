import os
import requests
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

# Fetch Bitcoin price from API
def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin",
        "vs_currencies": "usd"
    }
    headers = {
        "x-cg-pro-api-key": os.getenv("COINGECKO_API_KEY", "")
    }
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()
    return data["bitcoin"]["usd"]

# Save the fetched price into database
def save_to_database(price):
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "password")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "bitcoin_db")

    # Build connection string safely
    connection_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(connection_url)

    # Create a DataFrame to store
    df = pd.DataFrame({
        "timestamp": [datetime.utcnow()],
        "price": [price]
    })

    with engine.connect() as connection:
        df.to_sql("bitcoin_prices", con=connection, if_exists="append", index=False)

# Main
if __name__ == "__main__":
    try:
        bitcoin_price = fetch_bitcoin_price()
        save_to_database(bitcoin_price)
        print(f"[{datetime.utcnow()}] Successfully saved Bitcoin price: ${bitcoin_price}")
    except Exception as e:
        print(f"Error occurred: {e}")
