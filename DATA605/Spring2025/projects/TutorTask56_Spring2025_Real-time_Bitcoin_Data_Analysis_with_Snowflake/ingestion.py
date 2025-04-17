import os
import requests
import pandas as pd
from datetime import datetime
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fetch Bitcoin price from CoinGecko API
url = os.getenv("COINGECKO_API_URL")
response = requests.get(url)
price = response.json()['bitcoin']['usd']
timestamp = datetime.utcnow()

# Convert to DataFrame (optional but useful for further transformations)
df = pd.DataFrame([[timestamp, price]], columns=["timestamp", "price"])

# Get Snowflake connection details
account = os.getenv("SNOWFLAKE_ACCOUNT")
user = os.getenv("SNOWFLAKE_USER")
password = os.getenv("SNOWFLAKE_PASSWORD")
database = os.getenv("SNOWFLAKE_DATABASE")
schema = os.getenv("SNOWFLAKE_SCHEMA")
warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
table = os.getenv("SNOWFLAKE_TABLE")

# Connect to Snowflake
conn = snowflake.connector.connect(
    user=user,
    password=password,
    account=account,
    warehouse=warehouse,
    database=database,
    schema=schema
)

cursor = conn.cursor()

# Create the table if it doesn't exist (fully qualified name)
cursor.execute(f"""
CREATE TABLE IF NOT EXISTS {database}.{schema}.{table} (
    timestamp TIMESTAMP,
    price FLOAT
)
""")

# Insert the new record
cursor.execute(f"""
INSERT INTO {database}.{schema}.{table} (timestamp, price)
VALUES (%s, %s)
""", (timestamp, price))

print(f"✅ Inserted: {timestamp} - ${price}")

# Clean up
cursor.close()
conn.close()
