import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from prophet import Prophet
from typing import Tuple, Dict

class BitcoinAnalysisTool:
    def load_and_clean_data(self, csv_path: str) -> pd.DataFrame:
        df = pd.read_csv(csv_path)
        df.columns = [col.strip().lower() for col in df.columns]
        if 'price_usd' in df.columns:
            df = df.drop(columns=['price_usd'])
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df = df.sort_index()
        return df

    def plot_price_series(self, df: pd.DataFrame) -> None:
        plt.figure(figsize=(12, 5))
        plt.plot(df, label='Price')
        plt.title('Bitcoin Price Over Time')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)
        plt.show()

    def plot_rolling_stats(self, df: pd.DataFrame, window: int = 30) -> None:
        rolling_mean = df.rolling(window=window).mean()
        rolling_std = df.rolling(window=window).std()
        plt.figure(figsize=(12, 5))
        plt.plot(df, label='Price')
        plt.plot(rolling_mean, label=f'Rolling Mean ({window}d)')
        plt.plot(rolling_std, label=f'Rolling Std ({window}d)')
        plt.title('Rolling Statistics')
        plt.legend()
        plt.grid(True)
        plt.show()

    def decompose_series(self, df: pd.DataFrame, period: int = 30) -> None:
        decomp = seasonal_decompose(df, model='additive', period=period)
        decomp.plot()
        plt.show()

    def adf_test(self, df: pd.DataFrame) -> Dict[str, float]:
        series = df.dropna().iloc[:, 0]
        result = adfuller(series)
        return {
            "adf_statistic": result[0],
            "p_value": result[1],
            "is_stationary": result[1] < 0.05
        }

    def run_prophet_forecast(self, df: pd.DataFrame, periods: int = 30) -> Tuple[pd.DataFrame, pd.DataFrame]:
        df_prophet = df.reset_index()[['date', 'price']].rename(columns={'date': 'ds', 'price': 'y'})
        model = Prophet()
        model.fit(df_prophet)
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)
        return df_prophet, forecast

    def plot_prophet_forecast(self, df_prophet: pd.DataFrame, forecast: pd.DataFrame) -> None:
        df_prophet['ds'] = pd.to_datetime(df_prophet['ds'])
        forecast['ds'] = pd.to_datetime(forecast['ds'])
        plt.figure(figsize=(12, 5))
        plt.plot(df_prophet['ds'], df_prophet['y'], label='Actual')
        plt.plot(forecast['ds'], forecast['yhat'], label='Prophet Forecast')
        plt.title('Prophet Forecast vs Actual')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        plt.grid(True)
        plt.show()

    def generate_data_summary_report(self, df: pd.DataFrame) -> str:
        start_date = df.index.min().strftime("%Y-%m-%d")
        end_date = df.index.max().strftime("%Y-%m-%d")
        stats = df.describe().T
        summary = (
            f"📊 Bitcoin Price Data Summary\n"
            f"- Rows: {len(df)}\n"
            f"- Date Range: {start_date} to {end_date}\n"
            f"- Mean Price: {stats['mean'].values[0]:,.2f}\n"
            f"- Std Dev: {stats['std'].values[0]:,.2f}\n"
            f"- Min Price: {stats['min'].values[0]:,.2f}\n"
            f"- Max Price: {stats['max'].values[0]:,.2f}\n"
        )
        return summary

    def generate_stationarity_report(self, df: pd.DataFrame) -> str:
        result = self.adf_test(df)
        report = (
            f"📈 Stationarity Test (ADF)\n"
            f"- ADF Statistic: {result['adf_statistic']:.4f}\n"
            f"- p-value: {result['p_value']:.4f}\n"
            f"- Conclusion: {'✅ Series is stationary.' if result['is_stationary'] else '❌ Series is not stationary.'}"
        )
        return report

    def generate_forecast_report(self, forecast: pd.DataFrame, periods: int = 30) -> str:
        forecast_tail = forecast.tail(periods)
        min_forecast = forecast_tail["yhat"].min()
        max_forecast = forecast_tail["yhat"].max()
        mean_forecast = forecast_tail["yhat"].mean()
    
        report = (
            f"📅 Prophet Forecast Summary (Next {periods} Days)\n"
            f"- Forecast Range: {forecast_tail['ds'].min().date()} to {forecast_tail['ds'].max().date()}\n"
            f"- Min Forecast Price: {min_forecast:,.2f}\n"
            f"- Max Forecast Price: {max_forecast:,.2f}\n"
            f"- Avg Forecast Price: {mean_forecast:,.2f}"
        )
        return report


