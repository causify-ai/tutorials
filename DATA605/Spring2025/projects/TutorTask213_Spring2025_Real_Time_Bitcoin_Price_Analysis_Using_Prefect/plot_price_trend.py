from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

# ✅ Load environment variables from .env
load_dotenv()

# ✅ Retrieve the PostgreSQL URL from the .env file
POSTGRES_URL = os.getenv("POSTGRES_URL")

# ✅ Connect to the database
engine = create_engine(POSTGRES_URL)

# ✅ Query the latest 10 prices
df = pd.read_sql("SELECT * FROM prices ORDER BY timestamp DESC LIMIT 10", engine)
df = df[::-1]  # Reverse to show from oldest to newest

# ✅ Plot the price trend
plt.figure(figsize=(10, 6))
plt.plot(df["timestamp"], df["price"], marker='o')
plt.title("Bitcoin Price Trend")
plt.xlabel("Timestamp")
plt.ylabel("Price (USD)")
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()
