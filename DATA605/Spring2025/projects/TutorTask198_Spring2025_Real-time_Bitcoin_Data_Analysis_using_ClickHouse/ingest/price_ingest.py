from datetime import datetime
from config.clickhouse_client import client
from ingest.fetch_prices import (
    fetch_current_price,
    fetch_historical_prices,
    fetch_historical_hourly_prices,
)
import pandas as pd
import time


def ingest_historical_prices(days: int = 365, truncate: bool = False) -> None:
    """
    Insert historical Bitcoin prices into ClickHouse, ensuring no duplicate hourly entries.

    Args:
        days: Days of history to fetch.
        truncate: If True, clear existing data first.
    """
    if truncate:
        client.command("TRUNCATE TABLE bitcoin_db.price_data")

    # Fetch hourly points
    df = fetch_historical_hourly_prices(days)

    # Floor timestamps to the hour (deduplication key)
    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.floor("H")

    # Drop any rows with missing data
    df = df.dropna(subset=["timestamp", "price"])

    # Optional: remove duplicate timestamps (if any) within the fetched data
    df = df.drop_duplicates(subset="timestamp", keep="last")

    if not truncate and not df.empty:
        min_ts = df["timestamp"].min()
        max_ts = df["timestamp"].max()

        # Query existing timestamps in the same range
        result = client.query(
            """
            SELECT timestamp FROM bitcoin_db.price_data
             WHERE timestamp >= %(min_ts)s AND timestamp <= %(max_ts)s
            """,
            {"min_ts": min_ts, "max_ts": max_ts},
        )
        existing_ts = {row[0] for row in result.result_rows}
        df = df[~df["timestamp"].isin(existing_ts)]

    # Prepare rows for insertion
    if not df.empty:
        cleaned = list(
            df.itertuples(index=False, name=None)
        )  # [(timestamp, price), ...]
        client.insert("bitcoin_db.price_data", cleaned)
        print(f"✅ Inserted {len(cleaned)} new historical records.")
    else:
        print("📝 No new historical rows to insert.")


def ingest_current_price() -> None:
    """
    Insert the current Bitcoin price into ClickHouse, unless that hour already exists.
    """
    try:
        price = fetch_current_price()
    except RuntimeError as e:
        print(f"⚠️ Skipping current price insert: {e}")
        return

    timestamp = datetime.utcnow().replace(minute=0, second=0, microsecond=0)

    result = client.query(
        "SELECT count() FROM bitcoin_db.price_data WHERE timestamp = %(ts)s",
        {"ts": timestamp},
    )
    count = result.result_rows[0][0] if result.result_rows else 0

    if count == 0:
        client.command(
            "INSERT INTO bitcoin_db.price_data (timestamp, price) VALUES (%(ts)s, %(price)s)",
            {"ts": timestamp, "price": price},
        )
        print(f"✅ Inserted current price at {timestamp}: ${price}")
    else:
        print(f"🗓️  Row for {timestamp} already exists; skipping insert.")


def run_auto_ingest(interval_sec: int = 60) -> None:
    """
    Continuously ingest current price every `interval_sec`.

    Args:
        interval_sec: Seconds between fetches.
    """
    print(f"⏳ Auto-ingesting every {interval_sec}s. Ctrl+C to stop.")
    try:
        while True:
            ingest_current_price()
            time.sleep(interval_sec)
    except KeyboardInterrupt:
        print("🛑 Auto-ingest stopped.")
