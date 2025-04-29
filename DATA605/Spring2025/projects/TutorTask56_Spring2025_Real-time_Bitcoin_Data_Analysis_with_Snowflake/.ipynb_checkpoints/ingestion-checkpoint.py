import os
import requests
import pandas as pd
from datetime import datetime
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Step 1: Fetch 90-day historical BTC prices from CoinGecko
url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
params = {
    "vs_currency": "usd",
    "days": "90",
    "interval": "daily"
}
response = requests.get(url, params=params)
data = response.json()

# Step 2: Convert to DataFrame
prices = data["prices"]
df = pd.DataFrame(prices, columns=["timestamp", "price"])
df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

# Step 3: Load Snowflake credentials from .env
account = os.getenv("SNOWFLAKE_ACCOUNT")
user = os.getenv("SNOWFLAKE_USER")
password = os.getenv("SNOWFLAKE_PASSWORD")
database = os.getenv("SNOWFLAKE_DATABASE")
schema = os.getenv("SNOWFLAKE_SCHEMA")
warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
table = os.getenv("SNOWFLAKE_TABLE")

# Step 4: Connect to Snowflake
conn = snowflake.connector.connect(
    user=user,
    password=password,
    account=account,
    warehouse=warehouse,
    database=database,
    schema=schema
)
cursor = conn.cursor()

# Step 5: Create table if not exists
cursor.execute(f"""
CREATE TABLE IF NOT EXISTS {database}.{schema}.{table} (
    timestamp TIMESTAMP,
    price FLOAT
)
""")

# Step 6: Insert rows with proper timestamp conversion
inserted = 0
for _, row in df.iterrows():
    ts = row["timestamp"].to_pydatetime()  # Convert to Python datetime
    cursor.execute(f"""
    INSERT INTO {database}.{schema}.{table} (timestamp, price)
    VALUES (%s, %s)
    """, (ts, row["price"]))
    inserted += 1

print(f"Inserted {inserted} rows of 90-day BTC price data.")

# Step 7: Close connection
cursor.close()
conn.close()
df.to_csv("btc_price_history.csv", index=False)
print("Exported to btc_price_history.csv")