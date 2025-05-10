import os
import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_bitcoin_prices(days=7, interval='daily'):
    """
    Fetch historical Bitcoin price data from CoinGecko API.
    
    Args:
        days (int): Number of days of price data to fetch
        interval (str): Data interval ('daily' or 'hourly')
        
    Returns:
        pandas.DataFrame: DataFrame containing price data
    """
    try:
        # Calculate timestamps
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Convert to Unix timestamps (milliseconds)
        start_timestamp = int(start_date.timestamp() * 1000)
        end_timestamp = int(end_date.timestamp() * 1000)
        
        # Construct API URL
        url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range"
        params = {
            'vs_currency': 'usd',
            'from': start_timestamp // 1000,  # Convert to seconds
            'to': end_timestamp // 1000
        }
        
        # Make API request
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Convert price data to DataFrame
        prices_df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        prices_df['timestamp'] = pd.to_datetime(prices_df['timestamp'], unit='ms')
        
        # Add date and hour columns
        prices_df['date'] = prices_df['timestamp'].dt.date
        prices_df['hour'] = prices_df['timestamp'].dt.hour
        
        # Resample to daily data if requested
        if interval == 'daily':
            # Ensure timestamp is the index
            prices_df = prices_df.set_index('timestamp')
            # Resample and calculate mean price
            daily_prices = prices_df['price'].resample('D').mean()
            # Create new DataFrame with daily data
            prices_df = pd.DataFrame({
                'timestamp': daily_prices.index,
                'price': daily_prices.values,
                'date': daily_prices.index.date,
                'hour': 0
            })
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Save to CSV
        prices_df.to_csv('data/bitcoin_prices.csv', index=False)
        print(f"✅ Successfully fetched {len(prices_df)} price data points")
        
        return prices_df
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching price data from API: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ Error processing price data: {str(e)}")
        return None

if __name__ == "__main__":
    # Test the function
    fetch_bitcoin_prices()
