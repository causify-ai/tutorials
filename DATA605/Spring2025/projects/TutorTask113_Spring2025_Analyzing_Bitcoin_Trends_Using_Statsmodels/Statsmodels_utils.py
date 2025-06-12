""" 
statsmodels_utils.py

This file contains utility functions that support the tutorial notebooks.

- Notebooks should call these functions instead of writing raw logic inline.
- This helps keep the notebooks clean, modular, and easier to debug.
- Students should implement functions here for data preprocessing,
  model setup, evaluation, or any reusable logic.
""" 

import time
import pandas as pd
import requests
import matplotlib.pyplot as plt
import logging
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import yfinance as yf
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.arima.model import ARIMA
from pandas.plotting import lag_plot

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Function: Fetch and plot BTC data (1 year at 1H), save CSV, and produce time-series
# -----------------------------------------------------------------------------
def fetch_and_plot_btc_hourly(
    tickers: str = "BTC-USD",
    period: str = "1y",
    interval: str = "1h",
    csv_path: str = "btc_1yr_hourly.csv"
) -> pd.DataFrame:
    """
    Fetches BTC price data from Yahoo Finance for the last 1 year at hourly intervals,
    saves to CSV, and creates a time-series plot.

    Parameters
    ----------
    tickers : str
        Ticker symbol for yfinance (default "BTC-USD").
    period : str
        Data range period string (default "1y").
    interval : str
        Data interval (default "1h").
    csv_path : str
        Output CSV filename (default "btc_1yr_hourly.csv").

    Returns
    -------
    pd.DataFrame
        DataFrame indexed by Date with OHLCV columns.
    """
    # 1) Download 1 year of hourly data
    df = yf.download(tickers=tickers, period=period, interval=interval, progress=False)
    df.reset_index(inplace=True)
    df.to_csv(csv_path, index=False)

    # 2) Prepare for plotting
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df.set_index('Datetime', inplace=True)
    prices = df['Close']

    # 3) Time-series plot
    plt.figure(figsize=(12, 4))
    plt.plot(prices.index, prices.values, label='Close Price')
    plt.title(f"{tickers} — Last {period} @ {interval} Frequency")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    return df

# -----------------------------------------------------------------------------
# Function: Fetch and plot BTC data (15 years daily), save CSV, and produce time-series
# -----------------------------------------------------------------------------
def fetch_and_plot_btc_daily(
    tickers: str = "BTC-USD",
    period: str = "15y",
    interval: str = "1d",
    csv_path: str = "btc_15yr_daily.csv"
) -> pd.DataFrame:
    """
    Fetches BTC price data from Yahoo Finance for the last 15 years at daily intervals,
    saves to CSV, and creates a time-series plot.

    Parameters
    ----------
    tickers : str
        Ticker symbol for yfinance (default "BTC-USD").
    period : str
        Data range period string (default "15y").
    interval : str
        Data interval (default "1d").
    csv_path : str
        Output CSV filename (default "btc_15yr_daily.csv").

    Returns
    -------
    pd.DataFrame
        DataFrame indexed by Date with OHLCV columns.
    """
    # 1) Download 15 years of daily data
    df = yf.download(tickers=tickers, period=period, interval=interval, progress=False)
    df.reset_index(inplace=True)
    df.to_csv(csv_path, index=False)

    # 2) Prepare for plotting
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    prices = df['Close']

    # 3) Time-series plot
    plt.figure(figsize=(12, 4))
    plt.plot(prices.index, prices.values, label='Close Price')
    plt.title(f"{tickers} — Last {period} @ {interval} Frequency")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

    return df


# -----------------------------------------------------------------------------
# Function: Decompose and plot trend & seasonality of a time series
# -----------------------------------------------------------------------------
def plot_trend_and_seasonality(
    df: pd.DataFrame,
    column: str = "Close",
    period: int = 24,
    model: str = "additive",
    dpi: int = 100
) -> None:
    """
    Decomposes a time series into trend and seasonal components and plots them.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame indexed by datetime, containing the time series column.
    column : str
        Name of the column to decompose (default: "Close").
    period : int
        Seasonal period (e.g. 24 for daily cycle on hourly data).
    model : str
        Decomposition model: "additive" or "multiplicative".
    dpi : int
        Figure resolution (dots per inch; default: 100).

    Returns
    -------
    None
    """
    # 1) Decompose the series
    result = seasonal_decompose(df[column], model=model, period=period)

    # 2) Extract components
    original = df[column]
    trend    = result.trend
    seasonal = result.seasonal

    # 3) Plot original, trend, and seasonal components
    fig, axes = plt.subplots(3, 1, figsize=(15, 9), dpi=dpi, sharex=True)
    axes[0].plot(original)
    axes[0].set(title="Original Series", ylabel=column)

    axes[1].plot(trend)
    axes[1].set(title="Trend Component", ylabel=column)

    axes[2].plot(seasonal)
    axes[2].set(title="Seasonal Component", xlabel="Date", ylabel=column)

    plt.tight_layout()
    plt.show()


# -----------------------------------------------------------------------------
# Function: Run ADF and KPSS stationarity tests on a time series
# -----------------------------------------------------------------------------
def test_stationarity(ts: pd.Series) -> None:
    """
    Performs the Augmented Dickey–Fuller (ADF) and KPSS tests on a univariate time series.

    Parameters
    ----------
    ts : pd.Series
        Time series (indexed by datetime) to test for stationarity.

    Returns
    -------
    None
        Prints test statistics, p-values, and critical values for both ADF and KPSS.
    """
    # 1) ADF Test (null hypothesis: non-stationary)
    print(">>> Augmented Dickey–Fuller Test (H0: non-stationary)")
    adf_stat, adf_p, _, _, adf_crit, _ = adfuller(ts.dropna())
    print(f"ADF Statistic: {adf_stat:.4f}, p-value: {adf_p:.4f}")
    for level, crit in adf_crit.items():
        print(f"  Critical Value ({level}): {crit:.3f}")
    
    # 2) KPSS Test (null hypothesis: stationary)
    print("\n>>> KPSS Test (H0: stationary)")
    kpss_stat, kpss_p, _, kpss_crit = kpss(ts.dropna(), regression='c', nlags="auto")
    print(f"KPSS Statistic: {kpss_stat:.4f}, p-value: {kpss_p:.4f}")
    for level, crit in kpss_crit.items():
        print(f"  Critical Value ({level}): {crit:.3f}")

# -----------------------------------------------------------------------------
# Function: Difference a time series to remove trend / achieve stationarity
# -----------------------------------------------------------------------------
def detrend_series(ts, order: int = 1, plot: bool = False) -> pd.Series:
    """
    Differences the series to remove trend and help achieve stationarity.
    Accepts either a pandas Series or a single-column DataFrame.

    Parameters
    ----------
    ts : pd.Series or pd.DataFrame
        Original time series (indexed by datetime) or single-column DataFrame.
    order : int
        Number of differences to apply (default: 1).
    plot : bool
        If True, plots the differenced series.

    Returns
    -------
    pd.Series
        The differenced (detrended) series, with NaNs dropped.
    """
    # If passed a single-column DataFrame, extract the Series
    if isinstance(ts, pd.DataFrame):
        ts = ts.iloc[:, 0]

    detrended = ts.diff(order).dropna()

    if plot:
        plt.figure(figsize=(12, 4))
        plt.plot(detrended.index, detrended.values, label=f'Differenced (order={order})')
        plt.title(f'Detrended Series (order={order})')
        plt.xlabel('Date')
        ylabel = ts.name if hasattr(ts, 'name') and ts.name else 'Value'
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()

    return detrended


# -----------------------------------------------------------------------------
# Function: Fetch 1-day historical BTC data (1-min intervals)
# -----------------------------------------------------------------------------

def fetch_historical_data():
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": "1"}
    response = requests.get(url, params=params)
    try:
        data = response.json()
        prices = data["prices"]
    except KeyError:
        logger.error("Unexpected API response format.")
        logger.error(response.text)
        raise
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df.set_index("timestamp", inplace=True)
    df = df.resample("1min").mean().dropna()
    return df

# -----------------------------------------------------------------------------
# Function: Simulate real-time streaming
# -----------------------------------------------------------------------------

def simulate_realtime(df, minutes=3):
    logger.info(f"Simulating {minutes} minutes of real-time price updates...")
    for _ in range(minutes):
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
        price = response.json()['bitcoin']['usd']
        now = pd.Timestamp.utcnow()
        df.loc[now] = price
        logger.info(f"[{now}] Appended price: ${price}")
        time.sleep(60)
    return df

# -----------------------------------------------------------------------------
# Function: Plot raw BTC time series
# -----------------------------------------------------------------------------

def plot_time_series(df, title="Real-Time BTC Price (USD)"):
    """
    Plot the raw BTC price time series.

    :param df: DataFrame with a datetime index and 'price' column
    :param title: Title for the plot
    """
    df['price'].plot(figsize=(12, 4), title=title)
    plt.xlabel("Timestamp")
    plt.ylabel("Price (USD)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# -----------------------------------------------------------------------------
# Function: Fit ARIMA model and forecast customizable horizon
# -----------------------------------------------------------------------------

def run_arima_analysis(df):
    df = df.resample("1min").mean().ffill()
    model = ARIMA(df['price'], order=(2, 1, 2))
    results = model.fit()
    forecast = results.forecast(steps=30)
    return results, forecast

# -----------------------------------------------------------------------------
# Function: Plot forecast
# -----------------------------------------------------------------------------

def plot_forecast(df, forecast):
    plt.figure(figsize=(14, 6))
    plt.plot(df.index[-120:], df['price'].tail(120), label="Actual Price")
    forecast_index = pd.date_range(start=df.index[-1] + pd.Timedelta(minutes=1), periods=30, freq="1min")
    plt.plot(forecast_index, forecast, label="Forecast (Next 30 mins)", color="orange")
    plt.xlabel("Time (UTC)")
    plt.ylabel("BTC Price (USD)")
    plt.title("Bitcoin Price Forecast using ARIMA (UTC)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# -----------------------------------------------------------------------------
# Function: Save actual and forecast data to CSV
# -----------------------------------------------------------------------------

def save_to_csv(df, forecast):
    df.to_csv("btc_full_data.csv", index=True)
    forecast_index = pd.date_range(start=df.index[-1] + pd.Timedelta(minutes=1), periods=30, freq="1min")
    forecast_df = pd.DataFrame({"timestamp": forecast_index, "forecast_price": forecast.values})
    forecast_df.set_index("timestamp", inplace=True)
    forecast_df.to_csv("btc_price_forecast.csv", index=True)
    logger.info("Data saved to 'btc_full_data.csv' and 'btc_price_forecast.csv'.")

# -----------------------------------------------------------------------------
# Function: Plot ACF and PACF
# -----------------------------------------------------------------------------

def plot_acf_pacf(df, lags=40):
    plt.figure(figsize=(10, 4))
    plot_acf(df['price'], lags=lags)
    plt.title("Autocorrelation Function (ACF)")
    plt.tight_layout()
    plt.show()

    plt.figure(figsize=(10, 4))
    plot_pacf(df['price'], lags=lags, method='ywm')
    plt.title("Partial Autocorrelation Function (PACF)")
    plt.tight_layout()
    plt.show()

# -----------------------------------------------------------------------------
# Function: Plot lag plots for a time series
# -----------------------------------------------------------------------------
def plot_lag_series(
    df,
    column: str = "price",
    lags: int = 4,
    figsize: tuple = (10, 3),
    dpi: int = 100,
    color: str = "firebrick"
) -> None:
    """
    Creates side‐by‐side lag plots for the first `lags` lags of a series.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame indexed by datetime containing the series column.
    column : str
        Name of the column to lag‐plot (default "price").
    lags : int
        How many lag panels to draw (default 4).
    figsize : tuple
        Figure size (width, height) in inches.
    dpi : int
        Figure DPI.
    color : str
        Marker color for the scatter (default "firebrick").
    """
    plt.rcParams.update({'ytick.left': False, 'axes.titlepad': 10})
    fig, axes = plt.subplots(1, lags, figsize=figsize, sharex=True, sharey=True, dpi=dpi)
    for i in range(lags):
        lag_plot(df[column], lag=i+1, ax=axes[i], c=color)
        axes[i].set_title(f"Lag {i+1}")
    fig.suptitle(f"Lag Plots (first {lags} lags) of {column}", y=1.05)
    plt.tight_layout()
    plt.show()



# -----------------------------------------------------------------------------
# Function: Fetch and save BTC data for any time range (1, 30, 365 days)
# -----------------------------------------------------------------------------

def fetch_and_process_data(days: int, filename: str, title: str):
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": str(days)}
    response = requests.get(url, params=params)
    data = response.json()
    if "prices" not in data:
        logger.error(f"Unexpected response for {days} days.")
        logger.error(response.text)
        return None
    prices = data["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df.set_index("timestamp", inplace=True)
    if days == 1:
        df = df.resample("1min").mean()
    elif days == 30:
        df = df.resample("1H").mean()
    else:
        df = df.resample("1D").mean()
    df.dropna(inplace=True)
    df.to_csv(filename)
    logger.info(f"Saved data for {title} to {filename}")
    plt.figure(figsize=(12, 4))
    plt.plot(df.index, df["price"], label="Price (USD)")
    plt.title(f"Bitcoin Price - {title}")
    plt.xlabel("Time")
    plt.ylabel("Price (USD)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    return df
