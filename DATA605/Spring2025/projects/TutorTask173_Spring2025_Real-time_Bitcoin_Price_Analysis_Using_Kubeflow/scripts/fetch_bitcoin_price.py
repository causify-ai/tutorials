import os
import requests
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

# Fetch Bitcoin price
def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin",
        "vs_currencies": "usd"
    }
    headers = {
        "x-cg-pro-api-key": os.getenv("COINGECKO_API_KEY", "dummy_api_key")
    }
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    price = data["bitcoin"]["usd"]
    return price

# Save to TimescaleDB (or MySQL in Kubeflow)
def save_to_database(price):
    db_user = os.getenv("DB_USER", "user")
    db_password = os.getenv("DB_PASSWORD", "password")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "bitcoin_db")

    connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    engine = create_engine(connection_string)

    df = pd.DataFrame({
        "timestamp": [datetime.utcnow()],
        "price": [price]
    })

    with engine.connect() as conn:
        df.to_sql("bitcoin_prices", conn, if_exists="append", index=False)

# Main execution
if __name__ == "__main__":
    price = fetch_bitcoin_price()
    save_to_database(price)
    print(f"[Saved] Bitcoin price ${price} at {datetime.utcnow()}")
