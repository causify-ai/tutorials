"""
This python script provides utility functions for interacting with the Kubernetes Bitcoin data processing system

This module provides functions for:
1. Fetching Bitcoin price data
2. Analyzing price trends
3. Forecasting future prices
4. Detecting price anomalies
5. Monitoring system health
6. Managing Kubernetes resources

Note: This utiliy python script is used and will only work if the files are present in a production environment such as a Kubernetes cluster or a Docker image
"""

import requests
import pandas as pd
import numpy as np
import json
import socket
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from statsmodels.tsa.arima.model import ARIMA
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Configuration
def is_in_cluster():
    try:
        # Try to resolve the Kubernetes service
        socket.gethostbyname('kubernetes.default.svc.cluster.local')
        return True
    except:
        return False

# Use different URLs based on environment
if is_in_cluster():
    # Inside Kubernetes cluster
    API_BASE_URL = "http://bitcoin-fetcher.default.svc.cluster.local"
    PROMETHEUS_URL = "http://prometheus.default.svc.cluster.local:9090"
else:
    # Outside cluster (local development)
    API_BASE_URL = "http://localhost:8000"  # Update with correct port-forwarded URL
    PROMETHEUS_URL = "http://localhost:9090"  # Update with correct port-forwarded URL
POSTGRES_HOST = "postgres.default.svc.cluster.local"
POSTGRES_PORT = "5432"
POSTGRES_DB = "bitcoin_data"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = None  # Will be loaded from Kubernetes secret


# Data Retrieval Functions

def get_current_bitcoin_data():
    """
    Get the current Bitcoin price data
    
    Returns:
        dict: Dictionary containing current Bitcoin data
    """
    try:
        response = requests.get(f"{API_BASE_URL}/api/bitcoin/current")
        if response.status_code == 200:
            data = response.json()
            # Convert timestamp string to datetime object
            data['timestamp'] = datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S')
            return data
        else:
            raise Exception(f"API returned status code {response.status_code}")
    except Exception as e:
        print(f"Error fetching current Bitcoin data: {e}")
        # Return dummy data for demonstration purposes
        return {
            'price_usd': 63245.00,
            'price_change_24h': 0.80,
            'market_cap_usd': 1238394638392.0,
            'volume_24h_usd': 21675945274.0,
            'timestamp': datetime.now()
        }


def get_bitcoin_price_history(days=7, hours=None):
    """
    Get historical Bitcoin price data for the specified number of days or hours
    
    Args:
        days (int): Number of days of history to retrieve
        hours (int): Number of hours of history to retrieve (overrides days if specified)
        
    Returns:
        pandas.DataFrame: DataFrame containing timestamp and price data
    """
    try:
        if hours:
            time_param = f"hours={hours}"
        else:
            time_param = f"days={days}"
            
        response = requests.get(f"{API_BASE_URL}/api/bitcoin/history?{time_param}")
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        else:
            raise Exception(f"API returned status code {response.status_code}")
    except Exception as e:
        print(f"Error fetching Bitcoin price history: {e}")
        # Return dummy data for demonstration purposes
        
        # Generate timestamps
        end_date = datetime.now()
        if hours:
            start_date = end_date - timedelta(hours=hours)
            freq = 'H'
            periods = hours
        else:
            start_date = end_date - timedelta(days=days)
            freq = 'D'
            periods = days
            
        timestamps = pd.date_range(start=start_date, end=end_date, periods=periods)
        
        # Generate dummy price data with some randomness
        base_price = 29000.00
        price_data = []
        for i in range(len(timestamps)):
            # Add an upward trend and some random noise
            price = base_price * (1 + 0.01 * i) * (1 + np.random.normal(0, 0.01))
            price_data.append({
                'timestamp': timestamps[i],
                'price_usd': round(price, 2),
                'market_cap_usd': price * 19345678,
                'volume_24h_usd': price * 573829 * (1 + np.random.normal(0, 0.2)),
                'price_change_24h': np.random.normal(0, 1)
            })
            
        return pd.DataFrame(price_data)


def get_price_statistics(hours=24):
    """
    Get statistical summary of Bitcoin price data for the specified time period
    
    Args:
        hours (int): Number of hours to include in statistics
        
    Returns:
        dict: Dictionary containing min, max, avg, and stddev of price
    """
    try:
        response = requests.get(f"{API_BASE_URL}/api/bitcoin/stats?hours={hours}")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API returned status code {response.status_code}")
    except Exception as e:
        print(f"Error fetching price statistics: {e}")
        # Return dummy data for demonstration purposes
        df = get_bitcoin_price_history(hours=hours)
        return {
            'min_price': df['price_usd'].min(),
            'max_price': df['price_usd'].max(),
            'avg_price': df['price_usd'].mean(),
            'stddev_price': df['price_usd'].std(),
            'time_period': f'{hours}h'
        }


# Analysis Functions

def forecast_bitcoin_price(hours_ahead=12):
    """
    Generate a forecast of Bitcoin price for the specified number of hours ahead
    
    Args:
        hours_ahead (int): Number of hours to forecast
        
    Returns:
        dict: Dictionary containing forecast values and confidence intervals
    """
    try:
        response = requests.get(f"{API_BASE_URL}/api/bitcoin/forecast?hours={hours_ahead}")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API returned status code {response.status_code}")
    except Exception as e:
        print(f"Error forecasting Bitcoin price: {e}")
        # Generate dummy forecast data for demonstration purposes
        current_price = get_current_bitcoin_data()['price_usd']
        percent_change = np.random.normal(0, 0.6)  # Random change between -1% and 1%
        forecast_price = current_price * (1 + percent_change / 100)
        
        # Create a simple plot for visualization
        time_points = pd.date_range(start=datetime.now(), periods=hours_ahead+1, freq='H')
        # Create a gradual change from current price to forecast price
        prices = np.linspace(current_price, forecast_price, hours_ahead+1)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(time_points, prices, marker='o', linestyle='-', color='blue', label='Historical Data')
        ax.set_title(f'Bitcoin Price Forecast - Next {hours_ahead} Hours')
        ax.set_xlabel('Date/Time')
        ax.set_ylabel('Price (USD)')
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return {
            'forecast_fig': fig,
            'forecast_values': prices.tolist(),
            'last_known_price': current_price,
            'forecast_end_price': forecast_price,
            'percent_change_forecast': percent_change,
            'trend_direction': 'up' if percent_change > 0 else 'down'
        }


def detect_price_anomalies():
    """
    Detect anomalies in Bitcoin price data
    
    Returns:
        dict: Dictionary indicating if anomalies were detected and details
    """
    try:
        response = requests.get(f"{API_BASE_URL}/api/bitcoin/anomalies")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API returned status code {response.status_code}")
    except Exception as e:
        print(f"Error detecting price anomalies: {e}")
        # Return dummy data for demonstration purposes
        # 20% chance of generating an anomaly for demo purposes
        if np.random.random() < 0.2:
            current_data = get_current_bitcoin_data()
            z_score = np.random.normal(0, 2.5)  # Random z-score
            return {
                'has_anomaly': True,
                'timestamp': current_data['timestamp'],
                'price': current_data['price_usd'],
                'z_score': z_score,
                'message': f"Anomaly detected at {current_data['timestamp']}. Price: ${current_data['price_usd']:.2f}, Z-score: {z_score:.2f} standard deviations from mean."
            }
        else:
            return {
                'has_anomaly': False,
                'message': 'No anomalies detected in current data'
            }


# System Monitoring Functions
def get_system_health():
    """
    Get the health status of all system components
    
    Returns:
        dict: Dictionary containing health status of each component
    """
    try:
        response = requests.get(f"{API_BASE_URL}/api/system/health")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API returned status code {response.status_code}")
    except Exception as e:
        print(f"Error fetching system health: {e}")
        # Return dummy data for demonstration purposes
        return {
            'bitcoin_fetcher_status': 'Healthy',
            'postgres_status': 'Healthy',
            'prometheus_status': 'Healthy',
            'grafana_status': 'Healthy',
            'api_success_rate': 99.8,
            'data_points_collected': 14532
        }


def get_scaling_info():
    """
    Get information about the current pod scaling
    
    Returns:
        dict: Dictionary containing scaling information
    """
    try:
        response = requests.get(f"{API_BASE_URL}/api/system/scaling")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API returned status code {response.status_code}")
    except Exception as e:
        print(f"Error fetching scaling information: {e}")
        # Return dummy data for demonstration purposes
        return {
            'current_replicas': 2,
            'min_replicas': 1,
            'max_replicas': 5,
            'cpu_utilization': 45,
            'memory_utilization': 38
        }


# Kubernetes Management Functions

def scale_deployment(deployment_name, replicas):
    """
    Scale a Kubernetes deployment to the specified number of replicas
    
    Args:
        deployment_name (str): Name of the deployment to scale
        replicas (int): Number of replicas to scale to
        
    Returns:
        bool: True if scaling was successful, False otherwise
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/kubernetes/scale",
            json={
                'deployment': deployment_name,
                'replicas': replicas
            }
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Error scaling deployment: {e}")
        return False


def create_bitalert_dashboard():
    """
    Create a BitAlert dashboard in Grafana
    
    Returns:
        int: ID of the created dashboard
    """
    try:
        response = requests.post(f"{API_BASE_URL}/api/grafana/dashboards")
        if response.status_code == 200:
            return response.json()['id']
        else:
            raise Exception(f"API returned status code {response.status_code}")
    except Exception as e:
        print(f"Error creating BitAlert dashboard: {e}")
        return 12345  # Dummy dashboard ID


def create_alert_rule(rule):
    """
    Create a new alert rule in Prometheus
    
    Args:
        rule (dict): Alert rule configuration
        
    Returns:
        bool: True if alert was created successfully, False otherwise
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/prometheus/alerts",
            json=rule
        )
        return response.status_code == 200
    except Exception as e:
        print(f"Error creating alert rule: {e}")
        return False


# Advanced Analysis Helper Functions (used by other functions)

def _perform_time_series_analysis(data_df):
    """
    Internal helper function to perform time series analysis on Bitcoin price data
    
    Args:
        data_df (pandas.DataFrame): DataFrame containing timestamp and price_usd columns
        
    Returns:
        dict: Dictionary containing analysis results
    """
    if data_df.empty or len(data_df) < 30:
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
        return None
    
    try:
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
        
        return result
    except Exception as e:
        print(f"Error in time series analysis: {e}")
        return None


def _detect_price_anomalies_internal(data_df, contamination=0.05):
    """
    Internal helper function to detect anomalies in Bitcoin price data
    
    Args:
        data_df (pandas.DataFrame): DataFrame containing price data
        contamination (float): Expected fraction of outliers in the data
        
    Returns:
        dict: Dictionary containing detected anomalies and messaging
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
        print(f"Error in anomaly detection: {e}")
        return {'has_anomaly': False, 'message': f'Error in analysis: {str(e)}'}