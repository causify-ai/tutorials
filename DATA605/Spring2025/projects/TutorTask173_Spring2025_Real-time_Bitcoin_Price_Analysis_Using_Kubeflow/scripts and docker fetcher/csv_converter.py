import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from datetime import datetime

# PostgreSQL credentials
DB_USER = "postgres"
DB_PASSWORD = "testpass"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "bitcoin_db"

# Connect to TimescaleDB
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# Load all data
df = pd.read_sql("SELECT * FROM bitcoin_prices ORDER BY timestamp ASC", engine)

#  Print top 5 entries
print("\n Top 5 entries in DB:")
print(df.head())

#  Print total number of rows
print(f"\n Total records in 'bitcoin_prices': {len(df)} rows")

# Save CSV backup
df.to_csv("bitcoin_price_log_from_db.csv", index=False)
print(" Saved latest data to bitcoin_price_log_from_db.csv")

# Plotting (optional for real-time use)
plt.plot(df['timestamp'], df['price'], marker='o')
plt.xlabel("Timestamp")
plt.ylabel("Price (USD)")
plt.title("Bitcoin Price Over Time (from TimescaleDB)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
