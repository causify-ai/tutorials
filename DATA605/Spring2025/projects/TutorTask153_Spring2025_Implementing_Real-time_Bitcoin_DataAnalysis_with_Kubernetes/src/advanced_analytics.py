import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import logging

logger = logging.getLogger('bitcoin_fetcher')

def perform_time_series_analysis(data_df):
    """
    Perform time series analysis and forecasting on Bitcoin price data
    Returns a dict with results and matplotlib figure
    """
    try:
        if data_df.empty or len(data_df) < 30:
            logger.warning("Not enough data points for time series analysis")
            return None
            
        # Make sure timestamp is the index and data is sorted
        df = data_df.copy()
        if 'timestamp' in df.columns:
            df = df.set_index('timestamp')
        df = df.sort_index()
        
        # Resample to hourly data to handle irregular intervals
        df_hourly = df['price_usd'].resample('1H').mean().interpolate(method='linear')
        
        # Remove NaN values
        df_hourly = df_hourly.dropna()
        
        if len(df_hourly) < 24:  # Need at least a day of data
            logger.warning("Not enough hourly data points after resampling")
            return None
        
        # Fit ARIMA model
        # p=2 (AR), d=1 (differencing), q=2 (MA)
        model = ARIMA(df_hourly, order=(2, 1, 2))
        model_fit = model.fit()
        
        # Forecast next 12 hours
        forecast_steps = 12
        forecast = model_fit.forecast(steps=forecast_steps)
        
        # Calculate confidence intervals
        forecast_index = pd.date_range(
            start=df_hourly.index[-1], 
            periods=forecast_steps + 1, 
            freq='H'
        )[1:]
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot historical data (last 48 points)
        history_display = min(48, len(df_hourly))
        ax.plot(df_hourly.index[-history_display:], df_hourly.values[-history_display:], 
                label='Historical Data', color='blue')
        
        # Plot forecast
        ax.plot(forecast_index, forecast, label='Forecast', color='red')
        
        # Add labels and title
        ax.set_title('Bitcoin Price Forecast - Next 12 Hours')
        ax.set_xlabel('Date/Time')
        ax.set_ylabel('Price (USD)')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Get trend direction and strength
        short_term_change = ((forecast[-1] - df_hourly.iloc[-1]) / df_hourly.iloc[-1]) * 100
        trend_direction = "up" if short_term_change > 0 else "down"
        
        result = {
            'forecast_fig': fig,
            'forecast_values': forecast.tolist(),
            'last_known_price': df_hourly.iloc[-1],
            'forecast_end_price': forecast[-1],
            'percent_change_forecast': short_term_change,
            'trend_direction': trend_direction
        }
        
        logger.info(f"Time series analysis completed. Trend: {trend_direction} ({short_term_change:.2f}%)")
        return result
        
    except Exception as e:
        logger.error(f"Error in time series analysis: {e}")
        return None
    
def detect_price_anomalies(data_df, contamination=0.05):
    """
    Detect anomalies or outliers in Bitcoin price data
    Returns a dict with detected anomalies and messaging
    """
    try:
        if data_df.empty or len(data_df) < 10:
            return {'has_anomaly': False, 'message': 'Not enough data points'}
            
        # Prepare data
        df = data_df.copy()
        
        # Extract features relevant for anomaly detection
        features = ['price_usd', 'price_change_24h']
        if 'volume_24h_usd' in df.columns:
            features.append('volume_24h_usd')
        
        # Keep only complete rows
        df_features = df[features].dropna()
        
        if len(df_features) < 10:
            return {'has_anomaly': False, 'message': 'Not enough complete data points after removing NaNs'}
        
        # Standardize features
        scaler = StandardScaler()
        df_scaled = scaler.fit_transform(df_features)
        
        # Apply Isolation Forest for anomaly detection
        model = IsolationForest(contamination=contamination, random_state=42)
        df['anomaly'] = model.fit_predict(df_scaled)
        
        # -1 indicates anomaly, 1 indicates normal
        anomalies = df[df['anomaly'] == -1]
        
        if len(anomalies) > 0:
            # Get the most recent anomaly
            latest_anomaly = anomalies.iloc[-1]
            
            # Calculate how much the anomaly deviates from the mean
            mean_price = df['price_usd'].mean()
            std_price = df['price_usd'].std()
            z_score = (latest_anomaly['price_usd'] - mean_price) / std_price
            
            message = (
                f"Anomaly detected at {latest_anomaly['timestamp']}. "
                f"Price: ${latest_anomaly['price_usd']:.2f}, "
                f"Z-score: {z_score:.2f} standard deviations from mean."
            )
            
            return {
                'has_anomaly': True,
                'timestamp': latest_anomaly['timestamp'],
                'price': latest_anomaly['price_usd'],
                'z_score': z_score,
                'message': message
            }
        else:
            return {'has_anomaly': False, 'message': 'No anomalies detected in current data'}
        
    except Exception as e:
        logger.error(f"Error in anomaly detection: {e}")
        return {'has_anomaly': False, 'message': f'Error in analysis: {str(e)}'}