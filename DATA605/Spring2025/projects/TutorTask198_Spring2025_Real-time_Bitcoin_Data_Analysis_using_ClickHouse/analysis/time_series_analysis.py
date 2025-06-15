import pandas as pd
from config.clickhouse_client import client


def compute_moving_average(df: pd.DataFrame, window: int = 10) -> pd.DataFrame:
    """
    Compute a rolling moving average.

    Args:
        df: DataFrame with columns ['timestamp', 'price'].
        window: Number of periods for moving average.

    Returns:
        DataFrame with new column 'moving_avg'.
    """
    result = df.copy()
    result["moving_avg"] = result["price"].rolling(window=window).mean()
    return result


def detect_price_anomalies(
    df: pd.DataFrame, window: int = 10, threshold: float = 2.0
) -> pd.DataFrame:
    """
    Detect price anomalies based on deviation from moving average.

    Args:
        df: DataFrame with ['timestamp', 'price'].
        window: Window size for rolling statistics.
        threshold: Number of standard deviations to flag anomaly.

    Returns:
        DataFrame with 'anomaly' boolean column.
    """
    result = df.copy()
    ma = result["price"].rolling(window=window).mean()
    std = result["price"].rolling(window=window).std()
    result["anomaly"] = (result["price"] - ma).abs() > threshold * std
    return result


def fetch_time_series_from_db():
    """
    Fetches timestamp/price pairs from ClickHouse and returns a pandas DataFrame.
    """
    query = "SELECT timestamp, price FROM bitcoin_db.price_data ORDER BY timestamp"
    data = client.query_df(query)
    df = pd.DataFrame(data, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df
