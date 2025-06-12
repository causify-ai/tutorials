import os
import yaml
import pandas as pd
import requests
from datetime import datetime, timedelta, timezone
from griptape.tools import BaseTool
from attr import define, field
from typing import Any


@define
class BitcoinTool(BaseTool):
    config: dict = field()

    def read_checkpoint(self, path: str) -> str:
        if os.path.exists(path):
            with open(path, "r") as f:
                return yaml.safe_load(f).get("last_updated")
        return None

    def update_checkpoint(self, path: str, date_str: str):
        with open(path, "w") as f:
            yaml.dump({"last_updated": date_str}, f)

    def fetch_btc_data(self, start_date: datetime, end_date: datetime, api_key: str) -> pd.DataFrame:
        # Ensure both datetimes are timezone-aware UTC
        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=timezone.utc)
        if end_date.tzinfo is None:
            end_date = end_date.replace(tzinfo=timezone.utc)

        start_timestamp = int(start_date.timestamp())
        end_timestamp = int(end_date.timestamp())

        print(f"Fetching data from {start_date} → {start_timestamp}")
        print(f"To {end_date} → {end_timestamp}")

        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range"
        headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": api_key  # or "x-cg-pro-api-key" if using pro
        }

        response = requests.get(url, params={
            "vs_currency": "usd",
            "from": start_timestamp,
            "to": end_timestamp
        }, headers=headers)

        response.raise_for_status()
        data = response.json().get("prices", [])

        # Create DataFrame and keep timestamp as normalized pd.Timestamp
        df = pd.DataFrame(data, columns=["timestamp_ms", "price_usd"])
        df["timestamp"] = pd.to_datetime(df["timestamp_ms"], unit="ms")
        df["date"] = df["timestamp"].dt.normalize()  # Keep as Timestamp, strip time
        df = df[["date", "price_usd"]]
        return df

    def run(self, _: dict) -> str:
        csv_path = self.config["data_csv_path"]
        checkpoint_path = self.config["checkpoint_path"]
        default_start_date = self.config["default_start_date"]
        api_key = self.config["api_key"]

        # Read checkpoint or default start
        last_updated = self.read_checkpoint(checkpoint_path)
        if last_updated:
            start_date = pd.Timestamp(last_updated, tz=timezone.utc) + timedelta(days=1)
        else:
            start_date = pd.Timestamp(default_start_date, tz=timezone.utc)

        # End date = now - 24 hours to ensure up-to-date but not future
        end_date = pd.to_datetime(datetime.now(timezone.utc) - timedelta(hours=24))

        # Debug
        print("Last update:", last_updated, "| type:", type(last_updated))
        print("Start date:", start_date, "| type:", type(start_date))
        print("End date:", end_date, "| type:", type(end_date))

        # Stop if no data to fetch
        if start_date > end_date:
            return "No new data to fetch."

        # Fetch new BTC data
        new_df = self.fetch_btc_data(start_date, end_date, api_key)

        # Append to CSV
        if os.path.exists(csv_path):
            existing_df = pd.read_csv(csv_path, parse_dates=["date"])
            combined_df = pd.concat([existing_df, new_df])
        else:
            combined_df = new_df

        # Drop duplicates and sort by date (safe now)
        combined_df = combined_df.drop_duplicates(subset="date").sort_values("date")
        combined_df.to_csv(csv_path, index=False)

        # Update checkpoint
        last_date = combined_df["date"].max().strftime("%Y-%m-%d")
        self.update_checkpoint(checkpoint_path, last_date)

        return f"✅ Pipeline complete. Data updated to {last_date}."
