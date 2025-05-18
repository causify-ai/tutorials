import requests
import pandas as pd
from datetime import datetime, timezone
from storage.s3_handler import upload_json_to_s3
from config import AWS_BUCKET, DATA_PREFIX

def fetch_bitcoin(days=30, interval="daily"):
    try:
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
        params = {
            "vs_currency": "usd",
            "days": days,
            "interval": interval
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        result = response.json()

        prices = result.get("prices", [])
        if not prices:
            raise ValueError("No price data returned.")

        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)

        # Save to JSON format for consistency
        df_reset = df.reset_index()
        df_reset["timestamp"] = df_reset["timestamp"].dt.strftime('%Y-%m-%dT%H:%M:%S%z')
        data = df_reset.to_dict(orient="records")


        timestamp = datetime.now(timezone.utc).isoformat()
        filename = f"{DATA_PREFIX}price_{timestamp}.json"
        full_path = f"{AWS_BUCKET}/{filename}"

        upload_json_to_s3(full_path, data)
        print(f"✅ Uploaded {len(df)} data points to S3.")

    except Exception as e:
        print(f"❌ Ingestion failed: {e}")

# 👇 This ensures the function runs when you execute the script
if __name__ == "__main__":
    fetch_bitcoin(days=30)
