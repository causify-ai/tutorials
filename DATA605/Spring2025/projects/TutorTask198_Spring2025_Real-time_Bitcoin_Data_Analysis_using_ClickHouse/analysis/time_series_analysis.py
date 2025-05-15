import pandas as pd
from config.clickhouse_client import client
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error
import matplotlib.pyplot as plt
from typing import List

# from pmdarima import auto_arima


def compute_moving_averages(df: pd.DataFrame, days: List[int]) -> pd.DataFrame:
    """
    Compute moving averages over N days for hourly data.

    Args:
        df: DataFrame with columns ['timestamp', 'price'] (assumed hourly frequency).
        days: List of integers representing number of days (e.g., [7, 30]).

    Returns:
        DataFrame with additional columns like 'moving_average_7d', 'moving_average_30d', etc.
    """
    result = df.copy()
    for d in days:
        hours = d * 24  # Convert days to hours
        col_name = f"moving_average_{d}d"
        result[col_name] = result["price"].rolling(window=hours, min_periods=1).mean()
    return result


def detect_price_anomalies(
    df: pd.DataFrame, days: List[int] = None, threshold: float = 2.0
) -> pd.DataFrame:
    """
    Detect price anomalies for each N-day window based on deviation from rolling mean.

    Args:
        df: DataFrame with ['timestamp', 'price'] (hourly data expected).
        days: List of window sizes in days (e.g., [7, 30]).
        threshold: Std-dev multiple for anomaly detection.

    Returns:
        DataFrame with additional boolean columns like 'anomaly_7d', 'anomaly_30d'.
    """
    if days is None:
        days = [7]

    result = df.copy()
    for d in days:
        hours = d * 24
        rolling_mean = result["price"].rolling(window=hours, min_periods=1).mean()
        rolling_std = result["price"].rolling(window=hours, min_periods=1).std()
        col_name = f"anomaly_{d}d"
        result[col_name] = (
            result["price"] - rolling_mean
        ).abs() > threshold * rolling_std
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


def check_stationarity(df: pd.DataFrame) -> dict:
    """
    Run Augmented Dickey-Fuller test for stationarity.

    Args:
        df: DataFrame with 'Close' column.

    Returns:
        Dictionary with ADF statistic and p-value.
    """
    result = adfuller(df["price"])
    return {"adf_statistic": result[0], "p_value": result[1]}


def difference_series(df: pd.DataFrame) -> pd.Series:
    """
    Difference the time series to achieve stationarity.

    Args:
        df: DataFrame with 'Close' column.

    Returns:
        Series with first-order differencing.
    """
    return df["price"].diff().dropna()


# def forecast_with_arima(df: pd.DataFrame, order=(1, 1, 1), steps=30) -> pd.Series:
#     """
#     Forecast future values using ARIMA model.

#     Args:
#         df: DataFrame with 'Close' prices.
#         order: ARIMA order (p, d, q).
#         steps: Forecast horizon.

#     Returns:
#         Series with forecasted values.
#     """
#     if "timestamp" in df.columns:
#         df = df.set_index("timestamp")
#     df = df.resample("D").mean().dropna()

#     model = ARIMA(df["price"], order=order)
#     model_fit = model.fit()
#     forecast = model_fit.forecast(steps=steps)
#     return forecast


# def forecast_with_arima(df: pd.DataFrame, steps=30) -> pd.Series:
#     """
#     Forecast future values using ARIMA model.

#     Args:
#         df: DataFrame with 'Close' prices.
#         steps: Forecast horizon.

#     Returns:
#         Series with forecasted values.
#     """
#     if "timestamp" in df.columns:
#         df = df.set_index("timestamp")

#     df = df.resample("D").mean().dropna()

#     # Fit best model
#     model = auto_arima(
#         df["price"],
#         seasonal=False,
#         stepwise=True,
#         suppress_warnings=True,
#         error_action="ignore",
#     )
#     forecast = model.predict(n_periods=steps)
#     return pd.Series(
#         forecast,
#         index=pd.date_range(df.index[-1] + pd.Timedelta(days=1), periods=steps),
#     )


def forecast_with_prophet(df: pd.DataFrame, periods: int = 30) -> pd.DataFrame:
    """
    Forecast future values using Facebook Prophet.

    Args:
        df: DataFrame with ['timestamp', 'Close'].
        periods: Number of future periods (daily).

    Returns:
        Prophet forecast DataFrame.
    """
    df_daily = df.set_index("timestamp").resample("D").mean().dropna()

    if df_daily.shape[0] < 2:
        raise ValueError("Insufficient data for Prophet forecast")

    prophet_df = df_daily.reset_index().rename(
        columns={"timestamp": "ds", "price": "y"}
    )

    model = Prophet()
    model.fit(prophet_df)
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return forecast


def evaluate_forecast(actual: pd.Series, predicted: pd.Series) -> dict:
    """
    Evaluate forecast accuracy using MAE and MAPE.

    Args:
        actual: Actual values.
        predicted: Forecasted values.

    Returns:
        Dictionary with MAE and MAPE.
    """
    mae = mean_absolute_error(actual, predicted)
    mape = mean_absolute_percentage_error(actual, predicted)
    return {"mae": mae, "mape": mape}


def compute_bollinger_bands(
    df: pd.DataFrame, days: int = 20, num_std: float = 2.0
) -> pd.DataFrame:
    """
    Compute Bollinger Bands over a rolling window based on number of days.

    Args:
        df: DataFrame with ['timestamp', 'price'].
        days: Rolling window size in days (default: 20).
        num_std: Number of standard deviations.

    Returns:
        DataFrame with 'bb_upper' and 'bb_lower' columns.
    """
    result = df.copy()
    window = days * 24
    ma = result["price"].rolling(window=window, min_periods=1).mean()
    std = result["price"].rolling(window=window, min_periods=1).std()
    result["bb_upper"] = ma + num_std * std
    result["bb_lower"] = ma - num_std * std
    return result


def compute_rolling_stats(df: pd.DataFrame, days: List[int] = None) -> pd.DataFrame:
    """
    Compute rolling statistics: std, min, max over given day windows.

    Args:
        df: DataFrame with ['timestamp', 'price'].
        days: List of window sizes in days (default: [7, 14, 30]).

    Returns:
        DataFrame with rolling std, min, max columns.
    """
    if days is None:
        days = [7, 14, 30]

    result = df.copy()
    for d in days:
        h = d * 24
        result[f"std_{d}d"] = result["price"].rolling(window=h, min_periods=1).std()
        result[f"min_{d}d"] = result["price"].rolling(window=h, min_periods=1).min()
        result[f"max_{d}d"] = result["price"].rolling(window=h, min_periods=1).max()
    return result


def compute_daily_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute daily percentage returns from hourly data.

    Args:
        df: DataFrame with ['timestamp', 'price'].

    Returns:
        DataFrame with added 'daily_return' column.
    """
    result = df.copy()
    result["daily_return"] = result["price"].pct_change(periods=24) * 100
    return result
