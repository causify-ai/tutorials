import pandas as pd
from datetime import datetime

# Load the raw CSV
df = pd.read_csv('../data/btcusd_1-min_data.csv')

# Convert timestamp
df['timestamp'] = pd.to_datetime(df['Timestamp'], unit='s')

# Use 'Close' or 'Open' as price — adjust as needed
df['price_usd'] = df['Close'] if 'Close' in df.columns else df['Open']

# Keep only timestamp and price
df_clean = df[['timestamp', 'price_usd']]

# (Optional) Downsample to hourly
# df_clean = df_clean.set_index('timestamp').resample('1H').mean().reset_index()

# Save to a clean file
df_clean.to_csv('../data/bitcoin_historical_cleaned.csv', index=False)

print(f"✅ Cleaned historical data saved with {len(df_clean)} rows")
