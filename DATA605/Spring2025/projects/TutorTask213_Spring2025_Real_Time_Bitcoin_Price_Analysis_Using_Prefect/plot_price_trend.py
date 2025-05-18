from sqlalchemy import create_engine
import pandas as pd
import matplotlib.pyplot as plt

# ✅ Correct credentials
engine = create_engine("postgresql://sahithivankayala:sahithi2024@localhost:5432/bitcoin_etl")

df = pd.read_sql("SELECT * FROM prices ORDER BY timestamp DESC LIMIT 10", engine)
df = df[::-1]  # oldest to newest

plt.figure(figsize=(10, 6))
plt.plot(df["timestamp"], df["price"], marker='o')
plt.title("Bitcoin Price Trend")
plt.xlabel("Timestamp")
plt.ylabel("Price (USD)")
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()
plt.show()
