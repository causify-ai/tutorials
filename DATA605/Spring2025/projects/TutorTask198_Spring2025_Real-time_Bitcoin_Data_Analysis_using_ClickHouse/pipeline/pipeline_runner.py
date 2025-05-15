import pandas as pd
from config.clickhouse_client import client
from analysis.time_series_analysis import compute_moving_average, detect_price_anomalies


def run_pipeline(window: int = 10, threshold: float = 2.0) -> pd.DataFrame:
    """
    Fetch data from DB, compute analytics, return enriched DataFrame.

    Args:
        window: Rolling window for metrics.
        threshold: Std-dev threshold for anomalies.

    Returns:
        DataFrame with columns ['timestamp', 'price', 'moving_avg', 'anomaly'].
    """
    query = "SELECT timestamp, price FROM bitcoin_db.price_data ORDER BY timestamp"
    rows = client.query(query).result_rows
    df = pd.DataFrame(rows, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = compute_moving_average(df, window)
    df = detect_price_anomalies(df, window, threshold)
    return df
