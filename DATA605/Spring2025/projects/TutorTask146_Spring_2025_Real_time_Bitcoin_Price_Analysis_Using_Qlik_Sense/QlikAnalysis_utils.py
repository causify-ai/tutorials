import os
import requests
import pandas as pd
import subprocess
import logging
from datetime import datetime
from typing import List, Optional
import pytz

# Configure logging for the module
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

LOCAL_TIMEZONE = pytz.timezone('America/New_York')

def initialize_csv_file(filepath: str) -> None:
    """
    Create a CSV file with headers if it does not exist.

    Args:
        filepath (str): Path to the CSV file.
    """
    if not os.path.exists(filepath):
        pd.DataFrame(columns=["timestamp", "price_usd"]).to_csv(filepath, index=False)
        logging.info("Initialized CSV file with headers at %s", filepath)

def fetch_bitcoin_price() -> Optional[dict]:
    """
    Fetch the current Bitcoin price in USD from CoinGecko.

    Returns:
        Optional[dict]: Dictionary with 'timestamp' and 'price_usd', or None if failed.
    """
    api_url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        price = data.get('bitcoin', {}).get('usd')

        if price is not None:
            local_time = datetime.now(LOCAL_TIMEZONE).strftime("%Y-%m-%d %I:%M:%S")
            return {"timestamp": local_time, "price_usd": price}
        else:
            logging.warning("Received empty price data from API.")
    except requests.RequestException as req_exc:
        logging.error("Network/API error: %s", req_exc)
    except Exception as exc:
        logging.error("Unexpected error: %s", exc)
    return None

def append_to_csv(record: dict, filepath: str) -> None:
    """
    Append a single record to the CSV file.

    Args:
        record (dict): Dictionary containing a Bitcoin record.
        filepath (str): Path to the CSV file.
    """
    try:
        pd.DataFrame([record]).to_csv(filepath, mode='a', header=False, index=False)
        logging.info("Wrote record to CSV: %s", record)
    except Exception as exc:
        logging.error("Write error: %s", exc)

def push_csv_files_to_github(files: List[str], repo_dir: str) -> None:
    """
    Adds, commits, and pushes specified CSV files to GitHub.

    Args:
        files (List[str]): List of CSV file names to push.
        repo_dir (str): Path to the git repository directory.
    """
    try:
        os.chdir(repo_dir)
        logging.info("Changed working directory to %s", repo_dir)
        subprocess.run(["git", "add"] + files, check=True)
        commit_message = f"Auto-update at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push"], check=True)
        logging.info("Successfully pushed files to GitHub: %s", ", ".join(files))
    except subprocess.CalledProcessError as cpe:
        logging.error("Git command failed: %s", cpe)
    except Exception as exc:
        logging.error("Unexpected error: %s", exc)
from typing import Optional

def load_bitcoin_data(csv_path: str) -> pd.DataFrame:
    """
    Load and preprocess Bitcoin CSV data.

    Args:
        csv_path (str): Path to the bitcoin data CSV file.

    Returns:
        pd.DataFrame: Preprocessed DataFrame.
    """
    df = pd.read_csv(csv_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    return df

def add_time_series_features(df: pd.DataFrame, ma_window: int = 6, vol_window: int = 12) -> pd.DataFrame:
    """
    Adds moving average and volatility columns to a DataFrame.

    Args:
        df (pd.DataFrame): DataFrame with 'price_usd' and 'timestamp'.
        ma_window (int): Window for moving average.
        vol_window (int): Window for volatility.

    Returns:
        pd.DataFrame: DataFrame with new feature columns.
    """
    df['ma_6'] = df['price_usd'].rolling(window=ma_window).mean()
    df['volatility_12'] = df['price_usd'].rolling(window=vol_window).std()
    return df

def forecast_bitcoin(df: pd.DataFrame, periods: int = 24, freq: str = 'h') -> Optional[pd.DataFrame]:
    """
    Fit a Prophet model and forecast future Bitcoin prices.

    Args:
        df (pd.DataFrame): DataFrame with 'timestamp' and 'price_usd'.
        periods (int): Number of periods to forecast.
        freq (str): Frequency string for Prophet future dataframe.

    Returns:
        Optional[pd.DataFrame]: DataFrame with forecast results, or None if failed.
    """
    try:
        from prophet import Prophet
    except ImportError:
        logging.error("Prophet package is not installed.")
        return None

    df_prophet = df[['timestamp', 'price_usd']].rename(columns={'timestamp': 'ds', 'price_usd': 'y'})
    model = Prophet(daily_seasonality=True)
    model.fit(df_prophet)
    future = model.make_future_dataframe(periods=periods, freq=freq)
    forecast = model.predict(future)
    forecast_df = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    # Only future predictions
    forecast_df = forecast_df[forecast_df['ds'] > df_prophet['ds'].max()]
    return forecast_df

def save_dataframe(df: pd.DataFrame, csv_path: str) -> None:
    """
    Save a DataFrame to CSV.

    Args:
        df (pd.DataFrame): DataFrame to save.
        csv_path (str): Path to save the CSV file.
    """
    try:
        df.to_csv(csv_path, index=False)
        logging.info("Saved DataFrame to %s", csv_path)
    except Exception as exc:
        logging.error("Could not save DataFrame: %s", exc)
