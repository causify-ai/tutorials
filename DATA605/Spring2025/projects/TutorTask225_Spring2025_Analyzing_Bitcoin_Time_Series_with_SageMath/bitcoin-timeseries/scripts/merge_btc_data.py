import pandas as pd

# Load cleaned historical data
hist_df = pd.read_csv('../data/bitcoin_historical_cleaned.csv')
hist_df['timestamp'] = pd.to_datetime(hist_df['timestamp'])

# Load live BTC data
live_df = pd.read_csv('../data/bitcoin_live.csv')
live_df['timestamp'] = pd.to_datetime(live_df['timestamp'])

# Combine both
combined_df = pd.concat([hist_df, live_df])

# Drop duplicates (just in case) and sort chronologically
combined_df = combined_df.drop_duplicates(subset='timestamp')
combined_df = combined_df.sort_values('timestamp')

# Save to merged file
combined_df.to_csv('../data/bitcoin_timeseries.csv', index=False)

print(f"✅ Merged dataset saved with {len(combined_df)} rows.")
