# bitcoin_example.py

import pandas as pd
from prophet import Prophet
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.seasonal import seasonal_decompose
import matplotlib.pyplot as plt

def run_prophet_forecast(df, periods=60, freq='T'):
    # Prepare for Prophet
    df_prophet = df[['timestamp', 'price_usd']].rename(
        columns={'timestamp': 'ds', 'price_usd': 'y'}
    )
    df_prophet['ds'] = pd.to_datetime(df_prophet['ds'])

    # Fit Prophet
    model = Prophet(yearly_seasonality=False, weekly_seasonality=False, daily_seasonality=True)
    model.fit(df_prophet)

    # Create future frame & predict
    future = model.make_future_dataframe(periods=periods, freq=freq)
    forecast = model.predict(future)

    # Compute rolling metrics on forecast price (yhat)
    forecast['moving_avg_price'] = forecast['yhat'].rolling(window=7).mean()
    forecast['volatility_15m'] = forecast['yhat'].rolling(window=15).std()

    # Save to CSV for push script
    forecast.to_csv('forecast_prophet.csv', index=False)
    print("Saved Prophet forecast to forecast_prophet.csv")
    print("→ Prophet step complete")

    return forecast

def run_sarima_forecast(df, steps=60):
    # Fit a SARIMA(1,1,1)x(1,1,1,60) model
    sarima_model = SARIMAX(
        df['price_usd'],
        order=(1, 1, 1),
        seasonal_order=(1, 1, 1, 60),
        enforce_stationarity=False,
        enforce_invertibility=False
    ).fit(disp=False)

    # Forecast next `steps` points
    sarima_pred = sarima_model.get_forecast(steps=steps)
    sarima_df = sarima_pred.predicted_mean.reset_index()
    sarima_df.columns = ['ds', 'yhat_sarima']
    sarima_df.to_csv('forecast_sarima.csv', index=False)
    print("Saved SARIMA forecast to forecast_sarima.csv")
    print("→ SARIMA step complete")

    return sarima_df

def run_seasonal_decompose(df, period=60):
    df_indexed = df.set_index('timestamp')['price_usd'].asfreq('T').fillna(method='ffill')
    result = seasonal_decompose(df_indexed, model='additive', period=period)

    # Plot & save
    fig = result.plot()
    fig.set_size_inches(10, 8)
    plt.tight_layout()
    fig.savefig('seasonal_decompose.png')
    print("Saved seasonal decomposition plot to seasonal_decompose.png")
    print("→ Decompose step complete")

def main():
    # 1. Load full transformed history
    df = pd.read_csv('bitcoin_price_transformed_full.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # 2. Prophet forecast + rolling metrics
    forecast_prophet = run_prophet_forecast(df)

    # 3. SARIMA forecast
    _ = run_sarima_forecast(df)

    # 4. Seasonal decomposition
    run_seasonal_decompose(df)

if __name__ == '__main__':
    main()
