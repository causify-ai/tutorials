import requests
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime, timedelta
import statistics
import os
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA


def arrowify_data(data_dict: dict) -> pa.Table:
    batch = {k: [v] for k, v in data_dict.items()}
    return pa.table(batch)

def calculate_moving_average(table: pa.Table, window_size: int = 3) -> pa.Table:
    prices = table.column("price_usd").to_pylist()
    ma = [None if i < window_size - 1 else
          round(sum(prices[i - window_size + 1:i + 1]) / window_size, 2)
          for i in range(len(prices))]
    return table.append_column("moving_average", pa.array(ma))

def detect_anomalies(table: pa.Table, threshold: float = 2.0) -> pa.Table:
    prices = table.column("price_usd").to_pylist()
    mean = statistics.mean(prices)
    stdev = statistics.stdev(prices) if len(prices) > 1 else 0
    anomalies = [abs((p - mean) / stdev) > threshold if stdev else False for p in prices]
    return table.append_column("is_anomaly", pa.array(anomalies))

def save_to_parquet(table: pa.Table, path: str) -> None:
    pq.write_table(table, path)

def get_latest_timestamp_from_parquet(parquet_path: str) -> datetime:
    table = pq.read_table(parquet_path, columns=["timestamp"])
    timestamps = table.column("timestamp").to_pylist()
    return datetime.fromisoformat(max(timestamps))

def fetch_and_append_new_data(api_key: str, parquet_path: str):
    last_timestamp = get_latest_timestamp_from_parquet(parquet_path)
    next_time = int((last_timestamp + timedelta(hours=1)).timestamp())
    now_time = int(datetime.utcnow().timestamp())

    if next_time >= now_time:
        print("No new data to fetch.")
        return

    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range"
    headers = {"x-cg-demo-api-key": api_key}
    params = {
        "vs_currency": "usd",
        "from": str(next_time),
        "to": str(now_time)
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    records = [
        {
            "timestamp": datetime.utcfromtimestamp(ts / 1000).isoformat(),
            "price_usd": price
        }
        for ts, price in data.get("prices", [])
    ]

    if records:
        df = pd.DataFrame(records)
        new_table = pa.Table.from_pandas(df)
        existing_table = pq.read_table(parquet_path)
        combined_table = pa.concat_tables([existing_table, new_table])
        save_to_parquet(combined_table, parquet_path)
        print(f"Appended {len(records)} new rows.")
    else:
        print("No new records found.")

def create_log_entry(timestamp: datetime, num_rows: int, source: str, status: str, message: str = "") -> pa.Table:
    data = {
        "timestamp": [timestamp.isoformat()],
        "num_rows_loaded": [num_rows],
        "source": [source],
        "status": [status],
        "message": [message]
    }
    return pa.table(data)

def append_log_entry(log_table: pa.Table, log_path: str = "load_log.parquet"):
    if os.path.exists(log_path):
        existing = pq.read_table(log_path)
        combined = pa.concat_tables([existing, log_table])
    else:
        combined = log_table
    pq.write_table(combined, log_path)
    print("\n📋Loaded Log:")
    df = log_table.to_pandas()
    print(df.tail(10))

def generate_forecast_report(df: pd.DataFrame, output_path: str = "forecast_report.html"):
    df = df.copy()

    if 'timestamp' not in df.columns:
        raise ValueError("Missing 'timestamp' column in input DataFrame.")

    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df = df.dropna(subset=['timestamp'])
    df.set_index('timestamp', inplace=True)
    df.sort_index(inplace=True)

    df_daily = df['price_usd'].resample('D').mean().to_frame()

    # Calculate financial metrics
    df_daily['MA_7'] = df_daily['price_usd'].rolling(window=7).mean()
    df_daily['MA_30'] = df_daily['price_usd'].rolling(window=30).mean()
    df_daily['volatility_7'] = df_daily['price_usd'].rolling(window=7).std()
    df_daily['daily_return'] = df_daily['price_usd'].pct_change()

    model = ARIMA(df_daily['price_usd'].dropna(), order=(1, 1, 1))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=30)
    forecast_index = pd.date_range(start=df_daily.index[-1] + pd.Timedelta(days=1), periods=30)

    # Plot forecast
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    forecast_plot = output_path.replace(".html", "_forecast.png")
    plt.figure(figsize=(10, 4))
    plt.plot(df_daily['price_usd'], label="Historical")
    plt.plot(forecast_index, forecast, label="Forecast", color='orange')
    plt.title("Bitcoin Price Forecast")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(forecast_plot)
    plt.close()

    # Plot moving averages
    ma_plot = output_path.replace(".html", "_ma.png")
    plt.figure(figsize=(10, 4))
    plt.plot(df_daily['price_usd'], label='Price')
    plt.plot(df_daily['MA_7'], label='7-Day MA')
    plt.plot(df_daily['MA_30'], label='30-Day MA')
    plt.title("Moving Averages")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(ma_plot)
    plt.close()

    # Plot volatility
    vol_plot = output_path.replace(".html", "_vol.png")
    plt.figure(figsize=(10, 4))
    plt.plot(df_daily['volatility_7'], color='red')
    plt.title("7-Day Rolling Volatility")
    plt.xlabel("Date")
    plt.ylabel("Volatility")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(vol_plot)
    plt.close()

    # Save HTML report
    with open(output_path, "w") as f:
        f.write(f"""
        <html>
        <head><title>Bitcoin Forecast Report</title></head>
        <body>
        <h1>Bitcoin Price Forecast and Financial Metrics</h1>
        <p>Last updated: {pd.Timestamp.now()}</p>

        <h2>Forecast (ARIMA)</h2>
        <img src="{os.path.basename(forecast_plot)}" width="800"/>

        <h2>Moving Averages</h2>
        <img src="{os.path.basename(ma_plot)}" width="800"/>

        <h2>Volatility (7-Day)</h2>
        <img src="{os.path.basename(vol_plot)}" width="800"/>

        <h2>Returns Summary</h2>
        <p>Mean Daily Return: {df_daily['daily_return'].mean():.5f}</p>
        <p>Standard Deviation of Return: {df_daily['daily_return'].std():.5f}</p>
        </body>
        </html>
        """)

    print(f"\U0001F4C4 Forecast report saved to {output_path}")

