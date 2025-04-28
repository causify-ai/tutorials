"""
Real-time Bitcoin price ingestion and preprocessing pipeline using Luigi.

- Fetches live BTC-USD price data from the Coinbase WebSocket API.
- Cleans and formats data using Luigi task dependencies.
- Performs ARIMA-based forecasting and anomaly detection.

References:
- Coinbase WebSocket API documentation
- Luigi documentation: https://luigi.readthedocs.io/
"""
import luigi
import pandas as pd
import json
from datetime import datetime
import os
from statsmodels.tsa.arima.model import ARIMA


# Task 1: Fetch real-time BTC price data using WebSocket
class FetchDataTask(luigi.Task):
    """
    Task to stream BTC-USD price data from the Coinbase WebSocket API.

    :param date: date of execution
    :return: JSON file of raw price data
    """

    date = luigi.DateParameter(default=datetime.utcnow().date())

    def output(self):
        return luigi.LocalTarget(f"data/raw_{self.date}.json")

    def run(self):
        import asyncio
        import websockets

        async def fetch_prices():
            url = "wss://ws-feed.exchange.coinbase.com"
            product_id = "BTC-USD"
            data_list = []

            async with websockets.connect(url) as websocket:
                subscribe_msg = {
                    "type": "subscribe",
                    "channels": [
                        {"name": "ticker", "product_ids": [product_id]}
                    ]
                }
                await websocket.send(json.dumps(subscribe_msg))

                print("Fetching real BTC prices...")
                count = 0
                async for message in websocket:
                    msg = json.loads(message)
                    if msg["type"] == "ticker":
                        data_list.append({
                            "timestamp": msg["time"],
                            "price": float(msg["price"])
                        })
                        count += 1
                        if count >= 100:
                            break

            os.makedirs("data", exist_ok=True)
            with self.output().open("w") as f:
                json.dump(data_list, f)

        asyncio.run(fetch_prices())


# Task 2: Clean and format the data
class CleanDataTask(luigi.Task):
    """
    Task to clean and format the raw price data into a structured CSV.

    :param date: date of execution
    :return: CSV file with sorted timestamps
    """

    date = luigi.DateParameter(default=datetime.utcnow().date())

    def requires(self):
        return FetchDataTask(self.date)

    def output(self):
        return luigi.LocalTarget(f"data/clean_{self.date}.csv")

    def run(self):
        with self.input().open("r") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values("timestamp")

        df.to_csv(self.output().path, index=False)
    

# Task 3: Analyze time series, forecast using ARIMA, detect anomalies
class AnalyzeDataTask(luigi.Task):
    """
    Task to calculate rolling volatility, ARIMA forecast, and 
    Z-score anomalies.

    :param date: date of execution
    :return: CSV file with forecast and anomaly columns
    """

    date = luigi.DateParameter(default=datetime.utcnow().date())

    def requires(self):
        return CleanDataTask(self.date)

    def output(self):
        return luigi.LocalTarget(f"data/analyzed_{self.date}.csv")

    def run(self):
        df = pd.read_csv(self.input().path, parse_dates=["timestamp"])
        df['volatility'] = df['price'].rolling(window=10).std()
        model = ARIMA(df['price'], order=(2, 1, 2))
        results = model.fit()
        df['forecast'] = results.predict(start=10, end=len(df)-1, typ="levels")
        df['zscore'] = (df['price'] - df['price'].mean()) / df['price'].std()
        df['anomaly'] = df['zscore'].abs() > 3
        df.to_csv(self.output().path, index=False)
