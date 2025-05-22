from datetime import datetime
from utils import fetch_btc_data, save_to_parquet, query_parquet_summary_presto
from config import API_KEY  

# === CONFIG ===
START_DATE = datetime(2024, 1, 1)
PARQUET_PATH = "/data/warehouse/btc_data/btc_data.parquet"  # Hive-accessible

PRESTO_HOST = "localhost"
PRESTO_PORT = 8080
PRESTO_CATALOG = "hive"
PRESTO_SCHEMA = "default"
PRESTO_TABLE = "btc_data"

# === 1. Fetch Bitcoin Data ===
print("Fetching BTC data...")
df = fetch_btc_data(start_date=START_DATE, api_key=API_KEY)
print("Fetched rows:", len(df))

# === 2. Save to Parquet ===
print(f"Saving data to Parquet at: {PARQUET_PATH}")
save_to_parquet(df, PARQUET_PATH)

# === 3. Query via Presto ===
print("Querying Presto for summary...")
summary_df = query_parquet_summary_presto(
    presto_host=PRESTO_HOST,
    presto_port=PRESTO_PORT,
    catalog=PRESTO_CATALOG,
    schema=PRESTO_SCHEMA,
    table=PRESTO_TABLE
)

print("Summary of Bitcoin Prices by Date:")
print(summary_df.head())
