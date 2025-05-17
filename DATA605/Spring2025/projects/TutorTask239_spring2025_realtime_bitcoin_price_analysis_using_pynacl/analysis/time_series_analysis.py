import pandas as pd
import matplotlib.pyplot as plt
from crypto.encrypt import decrypt_data, sender_private, recipient_private
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime
from storage.db_handler import get_db, init_db
import time
import os
import json

def ensure_db_initialized():
    """Ensure database and tables are initialized"""
    try:
        init_db()
        # Verify tables exist
        with get_db() as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='btc_price'")
            if not cursor.fetchone():
                print("❌ Database tables not properly initialized. Please run main.py first to collect some data.")
                return False
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

def load_data(n_points=1000):
    """Load latest encrypted data from SQLite and decrypt"""
    if not ensure_db_initialized():
        return pd.DataFrame(columns=['timestamp', 'price'])

    try:
        with get_db() as conn:
            cursor = conn.execute(f"""
                SELECT timestamp, encrypted_price FROM btc_price
                ORDER BY timestamp DESC
                LIMIT {n_points}
            """)
            rows = cursor.fetchall()
        
        if not rows:
            print("⚠️ No data found in database. Waiting for data collection...")
            return pd.DataFrame(columns=['timestamp', 'price'])
        
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
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return pd.DataFrame(columns=['timestamp', 'price'])

def resample_data(df):
    """Resample to 1-minute intervals using mean price"""
    # Ensure index is datetime
    df.index = pd.to_datetime(df.index)
    # Resample and set frequency
    df_resampled = df.resample('1min').mean()
    return df_resampled

def perform_time_series_analysis(df):
    """Add Moving Averages, Volatility, Returns"""
    # Adjust window sizes based on available data
    data_points = len(df)
    print(f"📊 Available data points: {data_points}")
    
    if data_points < 2:
        print("⚠️ Not enough data points for meaningful analysis")
        return df
    
    # Use smaller windows if we have limited data
    ma_window = min(5, data_points - 1)  # Ensure window is smaller than data length
    vol_window = min(5, data_points - 1)
    
    print(f"📈 Using MA window size: {ma_window}")
    
    # Calculate indicators with adjusted windows
    df['MA_5'] = df['price'].rolling(window=ma_window, min_periods=1).mean()
    df['Volatility_5'] = df['price'].rolling(window=vol_window, min_periods=1).std()
    df['Returns'] = df['price'].pct_change(fill_method=None)
    
    # Only add MA_10 if we have enough data
    if data_points >= 10:
        df['MA_10'] = df['price'].rolling(window=10, min_periods=1).mean()
    else:
        df['MA_10'] = None
        print("ℹ️ Skipping MA_10 calculation - insufficient data points")
    
    # Drop any rows where price is NULL or invalid
    df = df.dropna(subset=['price'])
    df = df[df['price'] > 0]
    
    return df

def predict_future(df, steps=5):
    """Fit a basic ARIMA model and predict next 'steps' prices"""
    # Ensure the data is properly indexed with frequency
    price_data = df['price'].dropna()
    data_points = len(price_data)
    print(f"✅ Valid price points after resampling: {data_points}")

    # Adjust minimum required points based on ARIMA order
    min_points = 5  # Minimum points needed for basic analysis
    if data_points < min_points:
        print(f"❌ Not enough valid price data to fit ARIMA model! Need at least {min_points} points, got {data_points}")
        return pd.Series(dtype=float)

    # Use simpler ARIMA model for small datasets
    if data_points < 10:
        print("ℹ️ Using simpler ARIMA(1,1,1) model due to limited data")
        order = (1,1,1)
    else:
        order = (2,1,2)

    try:
        # Create a proper time series with frequency
        ts = pd.Series(price_data.values, index=price_data.index)
        
        # Fit ARIMA model
        model = ARIMA(ts, order=order)
        model_fit = model.fit()
        
        # Generate forecast
        forecast = model_fit.forecast(steps=steps)
        
        # Create proper datetime index for forecast
        last_date = ts.index[-1]
        forecast_dates = pd.date_range(
            start=last_date + pd.Timedelta(minutes=1),
            periods=steps,
            freq='1min'
        )
        forecast.index = forecast_dates
        
        print(f"✅ Successfully generated forecast for next {steps} minutes")
        return forecast
    except Exception as e:
        print(f"❌ Error in ARIMA forecasting: {e}")
        return pd.Series(dtype=float)

def save_analysis_to_db(df_analysis, df_forecast):
    """Save processed analysis and forecasts into SQLite"""
    with get_db() as conn:
        # Save analysis
        conn.execute("""
        CREATE TABLE IF NOT EXISTS btc_analysis (
            timestamp TIMESTAMP,
            price REAL,
            MA_5 REAL,
            MA_10 REAL,
            Volatility_5 REAL,
            Returns REAL
        )
        """)
        conn.execute("DELETE FROM btc_analysis")
        
        df_analysis = df_analysis.reset_index()
        # Drop any rows with NaT timestamps or NULL prices
        df_analysis = df_analysis.dropna(subset=['timestamp', 'price'])
        
        if df_analysis.empty:
            print("⚠️ No valid data to save to analysis table")
            return
            
        print(f"📊 Saving {len(df_analysis)} rows to analysis table")
        
        for _, row in df_analysis.iterrows():
            try:
                # Ensure all values are valid numbers
                price = float(row['price'])
                if pd.isna(price) or price <= 0:
                    continue
                    
                ma_5 = float(row['MA_5']) if pd.notnull(row['MA_5']) else None
                ma_10 = float(row['MA_10']) if pd.notnull(row['MA_10']) else None
                vol_5 = float(row['Volatility_5']) if pd.notnull(row['Volatility_5']) else None
                returns = float(row['Returns']) if pd.notnull(row['Returns']) else None
                
                # Only insert if we have a valid price
                conn.execute("""
                    INSERT INTO btc_analysis (timestamp, price, MA_5, MA_10, Volatility_5, Returns)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    row['timestamp'].isoformat(),
                    price,
                    ma_5,
                    ma_10,
                    vol_5,
                    returns
                ))
            except (ValueError, TypeError) as e:
                print(f"⚠️ Skipping invalid data row: {e}")
                continue
            except Exception as e:
                print(f"⚠️ Unexpected error saving row: {e}")
                continue

        # Save forecast
        conn.execute("""
        CREATE TABLE IF NOT EXISTS btc_forecast (
            timestamp TIMESTAMP,
            predicted_price REAL
        )
        """)
        conn.execute("DELETE FROM btc_forecast")

        if not df_forecast.empty:
            try:
                # Create forecast DataFrame with proper timestamps
                forecast_df = pd.DataFrame({
                    "timestamp": df_forecast.index,
                    "predicted_price": df_forecast.values
                })
                
                # Drop any rows with invalid predictions
                forecast_df = forecast_df.dropna()
                
                if not forecast_df.empty:
                    print(f"📈 Saving {len(forecast_df)} forecast predictions")
                    for _, row in forecast_df.iterrows():
                        if pd.notnull(row['timestamp']) and pd.notnull(row['predicted_price']):
                            predicted_price = float(row['predicted_price'])
                            if predicted_price > 0:  # Only save positive predictions
                                conn.execute("""
                                    INSERT INTO btc_forecast (timestamp, predicted_price)
                                    VALUES (?, ?)
                                """, (
                                    row['timestamp'].isoformat(),
                                    predicted_price
                                ))
                else:
                    print("⚠️ No valid forecast predictions to save")
            except Exception as e:
                print(f"⚠️ Error saving forecast: {e}")
        else:
            print("⚠️ No forecast data to save")

def ensure_plot_directory():
    """Ensure the plots directory exists"""
    plot_dir = 'static/plots'
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)
    return plot_dir

def plot_analysis(df, forecast):
    """Plot prices, moving averages, volatility, returns and forecast"""
    plot_dir = ensure_plot_directory()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Plot 1: Price and Moving Averages
    plt.figure(figsize=(14, 6))
    # Plot actual price
    if 'price' in df.columns and not df['price'].isna().all():
        valid_price = df[['price']].dropna()
        plt.plot(valid_price.index, valid_price['price'], label='Price', color='blue')

    # Plot 5-minute moving average
    if 'MA_5' in df.columns and not df['MA_5'].isna().all():
        valid_ma5 = df[['MA_5']].dropna()
        plt.plot(valid_ma5.index, valid_ma5['MA_5'], label='5-Min MA', color='orange')

    # Plot 10-minute moving average
    if 'MA_10' in df.columns and not df['MA_10'].isna().all():
        valid_ma10 = df[['MA_10']].dropna()
        plt.plot(valid_ma10.index, valid_ma10['MA_10'], label='10-Min MA', color='green')

    plt.title('BTC Price + Moving Averages')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'{plot_dir}/price_ma_{timestamp}.png')
    plt.close()

    # Plot 2: Volatility
    plt.figure(figsize=(14, 6))
    if 'Volatility_5' in df.columns and not df['Volatility_5'].isna().all():
        # Filter only non-NaN points
        valid_points = df[['Volatility_5']].dropna()

        plt.plot(valid_points.index, valid_points['Volatility_5'], color='red')
        plt.title('Rolling Volatility (5 Points)')
        plt.xlabel('Time')
        plt.ylabel('Volatility')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f'{plot_dir}/volatility_{timestamp}.png')

    plt.close()

    # Plot 3: Returns
    plt.figure(figsize=(14, 6))

    if 'Returns' in df.columns and not df['Returns'].isna().all():
        valid_returns = df[['Returns']].dropna()

        plt.plot(valid_returns.index, valid_returns['Returns'], color='green')
        plt.title('Returns (% Change)')
        plt.xlabel('Time')
        plt.ylabel('Returns')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f'{plot_dir}/returns_{timestamp}.png')

    plt.close()

    # Plot 4: Forecast
    if not forecast.empty:
        plt.figure(figsize=(14, 6))
        plt.plot(forecast.index, forecast.values, color='purple', marker='o', linestyle='dashed', label='Forecasted Price')
        plt.title('ARIMA Forecast (Next 5 Minutes)')
        plt.legend()
        plt.grid(True)
        plt.savefig(f'{plot_dir}/forecast_{timestamp}.png')
        plt.close()

    # Save the latest plot paths to a JSON file for the dashboard to read
    plot_paths = {
        'price_ma': f'price_ma_{timestamp}.png',
        'volatility': f'volatility_{timestamp}.png',
        'returns': f'returns_{timestamp}.png',
        'forecast': f'forecast_{timestamp}.png' if not forecast.empty else None,
        'timestamp': timestamp
    }
    
    with open(f'{plot_dir}/latest_plots.json', 'w') as f:
        json.dump(plot_paths, f)

    print(f"✅ Analysis plots saved with timestamp: {timestamp}")

if __name__ == "__main__":
    print("Running analysis...")
    df = load_data()
    
    if df.empty:
        print("⚠️ No data available for analysis. Waiting for data collection...")
        time.sleep(60)  # Wait a minute before retrying
        exit(0)
        
    df_resampled = resample_data(df)
    df_analysis = perform_time_series_analysis(df_resampled)
    forecast = predict_future(df_resampled)

    if not forecast.empty:
        save_analysis_to_db(df_analysis, forecast)

        forecast_df = pd.DataFrame({'price': forecast.values}, index=pd.date_range(start=df_analysis.index[-1]+pd.Timedelta(minutes=1), periods=len(forecast), freq='1min'))
        plot_analysis(df_analysis, forecast_df)
        print("✅ Analysis complete. Waiting 1 hour...")
    else:
        print("⚠️ Skipping saving and plotting because forecast is empty.")
