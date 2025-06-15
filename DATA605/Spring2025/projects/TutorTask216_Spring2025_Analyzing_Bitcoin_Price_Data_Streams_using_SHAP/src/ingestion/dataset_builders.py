import os
from datetime import datetime
from ingestion.fetch_data import fetch_market_chart_data

def save_dataset(df, folder, prefix):
    os.makedirs(folder, exist_ok=True)
    filename = f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    path = os.path.join(folder, filename)
    df.to_csv(path, index=False)
    print(f"[✓] Saved dataset to {path}")
    return df

def build_hourly_90d_dataset(config):
    df = fetch_market_chart_data(config, override_days=90)
    return save_dataset(df, folder="data/raw/hourly_90d", prefix="btc_hourly_90d")

def build_daily_max_dataset(config):
    df = fetch_market_chart_data(config, override_days=365)
    return save_dataset(df, folder="data/raw/daily_max", prefix="btc_daily_max")