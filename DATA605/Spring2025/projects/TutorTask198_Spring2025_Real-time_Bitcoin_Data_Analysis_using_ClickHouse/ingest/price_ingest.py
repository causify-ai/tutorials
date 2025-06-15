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
    Insert historical Bitcoin prices into ClickHouse, but only for timestamps
    not already present.

    Args:
        days: Days of history to fetch.
        truncate: If True, clear existing data first.
    """
    if truncate:
        client.command("TRUNCATE TABLE bitcoin_db.price_data")

    # fetch hourly points
    df = fetch_historical_hourly_prices(days)

    # build a list of (datetime, float) tuples
    cleaned = []
    for ts, price in zip(df["timestamp"], df["price"]):
        if ts is None or pd.isna(ts):
            continue
        if hasattr(ts, "to_pydatetime"):
            ts = ts.to_pydatetime()
        elif isinstance(ts, (int, float)):
            ts = datetime.utcfromtimestamp(int(ts))
        cleaned.append((ts, float(price)))

    if not truncate and cleaned:
        # determine range to query for existing data
        min_ts = min(ts for ts, _ in cleaned)
        max_ts = max(ts for ts, _ in cleaned)
        # pull existing timestamps in that window
        existing_ts_rows = client.execute(
            """
            SELECT timestamp
              FROM bitcoin_db.price_data
             WHERE timestamp >= %(min_ts)s
               AND timestamp <= %(max_ts)s
            """,
            {"min_ts": min_ts, "max_ts": max_ts},
        )
        existing_ts = {row[0] for row in existing_ts_rows}

        # filter out any that are already in the table
        cleaned = [(ts, price) for ts, price in cleaned if ts not in existing_ts]

    if cleaned:
        client.insert("bitcoin_db.price_data", cleaned)
    else:
        print("📝 No new historical rows to insert.")


def ingest_current_price() -> None:
    """
    Insert the current Bitcoin price into ClickHouse, unless that exact
    timestamp is already present.
    """
    price = fetch_current_price()
    timestamp = datetime.utcnow()

    # check for an existing row with this timestamp
    count = client.query(
        "SELECT count() FROM bitcoin_db.price_data WHERE timestamp = %(ts)s",
        {"ts": timestamp},
    )[0][0]

    if count == 0:
        client.command(
            "INSERT INTO bitcoin_db.price_data (timestamp, price) VALUES (%(ts)s, %(price)s)",
            {"ts": timestamp, "price": price},
        )
    else:
        print(f"🗓️  Row for {timestamp!r} already exists; skipping insert.")


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
