import os
import pandas as pd
import matplotlib.pyplot as plt
from docker_sdk_utils import CryptoDataFetcher

INFLUXDB_URL = os.environ['INFLUXDB_URL']
INFLUXDB_TOKEN = os.environ['INFLUXDB_TOKEN']
INFLUXDB_ORG = os.environ['INFLUXDB_ORG']
INFLUXDB_BUCKET = os.environ['INFLUXDB_BUCKET']

def main():
    fetcher = CryptoDataFetcher(
        influxdb_url=INFLUXDB_URL,
        influxdb_token=INFLUXDB_TOKEN,
        influxdb_org=INFLUXDB_ORG,
        influxdb_bucket=INFLUXDB_BUCKET
    )
    data = fetcher.query_data(start="-60m")
    if data:
        df = pd.DataFrame(data)
        close_prices = df[df['field'] == 'close'][['time', 'value']].sort_values('time')
        ts_df = fetcher.time_series_analysis(close_prices.reset_index(drop=True), order=(1, 1, 1), window=5)
        plt.figure(figsize=(10, 4))
        plt.plot(ts_df['time'], ts_df['value'], label='Close Price')
        plt.plot(ts_df['time'], ts_df['moving_avg'], label='Moving Avg (5)')
        if ts_df['arima_forecast'].notnull().any():
            plt.plot(ts_df['time'], ts_df['arima_forecast'], label='ARIMA Forecast', linestyle='--')
        plt.title('BTC/USD Close Price: Moving Avg & ARIMA')
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.savefig('/output/btc_analysis.png')
        print("Plot saved to /output/btc_analysis.png")
    else:
        print("No data found in InfluxDB.")

if __name__ == "__main__":
    main()