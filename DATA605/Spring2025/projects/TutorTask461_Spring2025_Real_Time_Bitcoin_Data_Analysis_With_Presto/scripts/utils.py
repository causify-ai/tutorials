import os
import requests
import pandas as pd
from datetime import datetime, timezone
from pyhive import presto  # make sure to install: pip install pyhive[presto]


def fetch_btc_data(start_date: datetime, api_key: str) -> pd.DataFrame:
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)
    end_date = datetime.now(timezone.utc)

    start_timestamp = int(start_date.timestamp())
    end_timestamp = int(end_date.timestamp())

    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range"
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": api_key
    }

    response = requests.get(url, params={
        "vs_currency": "usd",
        "from": start_timestamp,
        "to": end_timestamp
    }, headers=headers)
    response.raise_for_status()

    data = response.json().get("prices", [])
    df = pd.DataFrame(data, columns=["timestamp_ms", "price_usd"])
    df["timestamp"] = pd.to_datetime(df["timestamp_ms"], unit="ms")
    df["date"] = df["timestamp"].dt.normalize()
    df = df[["date", "price_usd"]]

    return df


def save_to_parquet(df: pd.DataFrame, path: str) -> None:
    df.to_parquet(path, index=False)
    print(f"Data saved to: {path}")


def query_parquet_summary_presto(presto_host: str, presto_port: int, catalog: str, schema: str, table: str) -> pd.DataFrame:
    conn = presto.connect(
        host=presto_host,
        port=presto_port,
        catalog=catalog,
        schema=schema
    )
    cursor = conn.cursor()

    query = f"""
    SELECT 
        date, 
        MIN(price_usd) AS min_price,
        MAX(price_usd) AS max_price,
        AVG(price_usd) AS avg_price
    FROM {table}
    GROUP BY date
    ORDER BY date
    """

    cursor.execute(query)
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    return pd.DataFrame(rows, columns=columns)
