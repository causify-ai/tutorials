import requests
import json
import os
import pandas as pd
import luigi
from datetime import datetime, timezone
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt
import boto3
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()


def fetch_btc_price_history(days=2):
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
    }
    headers = {"User-Agent": "BTC-Pipeline"}
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    data = response.json()

    prices = data["prices"]
    import pandas as pd
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df


def save_to_json(df, path):
    records = df.copy()
    records["timestamp"] = records["timestamp"].astype(
        str
    )  # Convert to string
    with open(path, "w") as f:
        json.dump(records.to_dict(orient="records"), f)


def read_json(path):
    import json
    with open(path, "r") as f:
        data = json.load(f)
    return pd.DataFrame(data)


class FetchDataTask(luigi.Task):
    date = luigi.DateParameter(default=datetime.now(timezone.utc).date())

    def output(self):
        return luigi.LocalTarget(f"data/raw_{self.date}.json")

    def run(self):
        df = fetch_btc_price_history(days=2)
        if df.empty:
            raise ValueError("No data returned from Coingecko API.")
        save_to_json(df, self.output().path)


class CleanDataTask(luigi.Task):
    date = luigi.DateParameter(default=datetime.utcnow().date())

    def requires(self):
        return FetchDataTask(self.date)
    
    def output(self):
        return luigi.LocalTarget(f"data/clean_{self.date}.csv")
    
    def run(self):
        df = read_json(self.input().path)
        df = df.sort_values("timestamp")
        df.to_csv(self.output().path, index=False)


class AnalyzeDataTask(luigi.Task):
    date = luigi.DateParameter(default=datetime.utcnow().date())

    def requires(self):
        return CleanDataTask(self.date)
    
    def output(self):
        return luigi.LocalTarget(f"data/analyzed_{self.date}.csv")
    
    def run(self):
        df = pd.read_csv(self.input().path, parse_dates=["timestamp"])
        df["volatility"] = df["price"].rolling(window=10).std()
        model = ARIMA(df["price"], order=(2, 1, 2))
        results = model.fit()
        df["forecast"] = results.predict(start=10, end=len(df)-1, typ="levels")
        df["zscore"] = (df["price"] - df["price"].mean()) / df["price"].std()
        df["anomaly"] = df["zscore"].abs() > 3
        df.to_csv(self.output().path, index=False)


class VisualizeDataTask(luigi.Task):
    date = luigi.DateParameter(default=datetime.utcnow().date())

    def requires(self):
        return AnalyzeDataTask(self.date)
    
    def output(self):
        return {
            "price_forecast": luigi.LocalTarget(
                (
                    f"data/plot_price_forecast_"
                    f"{self.date}.png"
                )
            ),
            "volatility": luigi.LocalTarget(
                f"data/plot_volatility_{self.date}.png"
            ),
            "zscore": luigi.LocalTarget(f"data/plot_zscore_{self.date}.png"),
            "error": luigi.LocalTarget(
                f"data/plot_forecast_error_{self.date}.png"
            )
        }
    
    def run(self):
        df = pd.read_csv(self.input().path, parse_dates=["timestamp"])
        # 1. Price + Forecast + Anomalies
        plt.figure(figsize=(12, 4))
        plt.plot(df['timestamp'], df['price'], label='Price')
        plt.plot(
            df['timestamp'],
            df['forecast'],
            label='Forecast',
            linestyle='--'
        )
        plt.scatter(
            df[df['anomaly']]['timestamp'], 
            df[df['anomaly']]['price'], 
            color='red', 
            label='Anomaly'
        )
        plt.title("Price, Forecast, and Anomalies")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(self.output()["price_forecast"].path)
        plt.close()

        # 2. Volatility
        plt.figure(figsize=(12, 4))
        plt.plot(df['timestamp'], df['volatility'], color='orange')
        plt.title("1-Hour Rolling Volatility")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(self.output()["volatility"].path)
        plt.close()

        # 3. Z-Score Histogram:
        # This section generates a histogram of Z-scores to visualize
        # the distribution and identify anomalies.
        plt.figure(figsize=(8, 4))
        plt.hist(
            df['zscore'].dropna(), 
            bins=30, 
            color='skyblue', 
            edgecolor='black'
        )
        plt.axvline(3, color='red', linestyle='--')
        plt.axvline(-3, color='red', linestyle='--')
        plt.title("Z-Score Distribution")
        plt.tight_layout()
        plt.savefig(self.output()["zscore"].path)
        plt.close()

        # 4. Forecast Error
        df["error"] = df["price"] - df["forecast"]
        plt.figure(figsize=(12, 4))
        plt.plot(df["timestamp"], df["error"], color="purple")
        plt.title("Forecast Error Over Time")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(self.output()["error"].path)
        plt.close()


class AlertTask(luigi.Task):
    date = luigi.DateParameter(default=datetime.utcnow().date())

    def requires(self):
        return AnalyzeDataTask(self.date)
    
    def output(self):
        return luigi.LocalTarget(f"data/alert_{self.date}.txt")
    
    def run(self):
        df = pd.read_csv(self.input().path)
        anomalies = df[df["anomaly"]]
        alert_message = ""
        if not anomalies.empty:
            alert_message = (
                (
                    f"ALERT: Anomalies detected on {self.date}:\n"
                    + "\n".join(
                        anomalies['timestamp'].astype(str).tolist()
                    )
                )
            )
            print(alert_message)
            msg = EmailMessage()
            msg.set_content(alert_message)
            msg["Subject"] = f"BTC Alert {self.date}"
            msg["From"] = os.getenv("ALERT_EMAIL_FROM")
            msg["To"] = os.getenv("ALERT_EMAIL_TO")
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(
                    os.getenv("ALERT_EMAIL_FROM"), 
                    os.getenv("ALERT_EMAIL_PASSWORD")
                )
                smtp.send_message(msg)
        else:
            alert_message = "✅ No anomalies detected."
        with self.output().open("w") as f:
            f.write(alert_message)


class StoreToS3Task(luigi.Task):
    date = luigi.DateParameter(default=datetime.utcnow().date())

    def requires(self):
        return AnalyzeDataTask(self.date)
    
    def output(self):
        return luigi.LocalTarget(f"data/uploaded_{self.date}.txt")
    
    def run(self):
        bucket = os.getenv("S3_BUCKET")
        key = f"bitcoin/analytics/analyzed_{self.date}.csv"
        filepath = self.input().path
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        s3.upload_file(filepath, bucket, key)
        with self.output().open("w") as f:
            f.write(f"Uploaded to s3://{bucket}/{key}")
