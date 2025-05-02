
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
from crypto.encrypt import decrypt_data, sender_private, recipient_private
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime

def load_data(n_points=1000):
    """Load latest encrypted data from DuckDB and decrypt"""
    conn = duckdb.connect("btc_data.duckdb", read_only=True)
    
    rows = conn.execute(f"""
        SELECT timestamp, encrypted_price FROM btc_price
        ORDER BY timestamp DESC
        LIMIT {n_points}
    """).fetchall()
    
    conn.close()
    
    # Decrypt
    data = []
    for ts, enc in reversed(rows):
        try:
            price = float(decrypt_data(enc, sender_private.public_key, recipient_private))
            data.append((ts, price))
        except Exception as e:
            print(f"Skipping bad data: {e}")
            continue

    df = pd.DataFrame(data, columns=['timestamp', 'price'])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    return df.dropna()

def resample_data(df):
    """Resample to 1-minute intervals using mean price"""
    df_resampled = df.resample('1min').mean()
    df_resampled.index.freq = 'T'
    return df_resampled

def perform_time_series_analysis(df):
    """Add Moving Averages, Volatility, Returns"""
    df['MA_5'] = df['price'].rolling(window=5).mean()
    df['MA_10'] = df['price'].rolling(window=10).mean()
    df['Volatility_5'] = df['price'].rolling(window=5).std()
    df['Returns'] = df['price'].pct_change(fill_method=None)
    return df

def predict_future(df, steps=5):
    """Fit a basic ARIMA(2,1,2) model and predict next 'steps' prices"""
    price_data = df['price'].dropna()

    print(f"✅ Valid price points after resampling: {len(price_data)}")

    if price_data.empty or len(price_data) < 10:
        print("❌ Not enough valid price data to fit ARIMA model! Skipping forecast.")
        return pd.Series(dtype=float)

    model = ARIMA(price_data, order=(2,1,2))
    model_fit = model.fit()

    forecast = model_fit.forecast(steps=steps)
    return forecast

def save_analysis_to_duckdb(df_analysis, df_forecast):
    """Save processed analysis and forecasts into DuckDB"""
    conn = duckdb.connect("btc_data.duckdb")

    # Save analysis
    conn.execute("""
    CREATE TABLE IF NOT EXISTS btc_analysis (
        timestamp TIMESTAMP,
        price DOUBLE,
        MA_5 DOUBLE,
        MA_10 DOUBLE,
        Volatility_5 DOUBLE,
        Returns DOUBLE
    )
    """)
    conn.execute("DELETE FROM btc_analysis")
    df_analysis = df_analysis.reset_index()
    conn.execute("INSERT INTO btc_analysis SELECT * FROM df_analysis")

    # Save forecast
    conn.execute("""
    CREATE TABLE IF NOT EXISTS btc_forecast (
        timestamp TIMESTAMP,
        predicted_price DOUBLE
    )
    """)
    conn.execute("DELETE FROM btc_forecast")

    forecast_df = pd.DataFrame({
        "timestamp": pd.date_range(start=df_analysis['timestamp'].iloc[-1]+pd.Timedelta(minutes=1), periods=len(df_forecast), freq='1min'),
        "predicted_price": df_forecast.values
    })
    conn.execute("INSERT INTO btc_forecast SELECT * FROM forecast_df")

    conn.close()

def plot_analysis(df, forecast):
    """Plot prices, moving averages, volatility, returns and forecast"""
    plt.figure(figsize=(14, 10))

    # Plot prices and moving averages
    plt.subplot(4, 1, 1)
    plt.plot(df.index, df['price'], label='Price')
    plt.plot(df.index, df['MA_5'], label='5-Min MA')
    plt.plot(df.index, df['MA_10'], label='10-Min MA')
    plt.title('BTC Price + Moving Averages')
    plt.legend()

    # Plot volatility
    plt.subplot(4, 1, 2)
    plt.plot(df.index, df['Volatility_5'], color='red')
    plt.title('Rolling Volatility (5 Points)')

    # Plot returns
    plt.subplot(4, 1, 3)
    plt.plot(df.index, df['Returns'], color='green')
    plt.title('Returns (% Change)')

    # Plot forecast
    plt.subplot(4, 1, 4)
    plt.plot(forecast.index, forecast.values, color='purple', marker='o', linestyle='dashed', label='Forecasted Price')
    plt.title('ARIMA Forecast (Next 5 Minutes)')
    plt.legend()

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    df = load_data()
    df_resampled = resample_data(df)
    df_analysis = perform_time_series_analysis(df_resampled)
    forecast = predict_future(df_resampled)

    if not forecast.empty:
        save_analysis_to_duckdb(df_analysis, forecast)

        forecast_df = pd.DataFrame({'price': forecast.values}, index=pd.date_range(start=df_analysis.index[-1]+pd.Timedelta(minutes=1), periods=len(forecast), freq='1min'))
        plot_analysis(df_analysis, forecast_df)
    else:
        print("⚠️ Skipping saving and plotting because forecast is empty.")
