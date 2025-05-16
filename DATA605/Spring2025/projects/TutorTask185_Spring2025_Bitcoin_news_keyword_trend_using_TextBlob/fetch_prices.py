import os
import requests
import pandas as pd
import time
from datetime import datetime, timedelta
import json
import urllib.request
import urllib.error

def fetch_current_bitcoin_price():
    """
    Fetch the current Bitcoin price and related metrics from CoinGecko API.
    
    Returns:
        dict: Dictionary with current price data or None if error
    """
    try:
        print("  → Fetching current Bitcoin price...")
        current_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true"
        current_response = requests.get(current_url, timeout=10)
        if current_response.status_code == 200:
            current_data = current_response.json()
            if 'bitcoin' in current_data:
                current_price = {
                    'price': current_data['bitcoin']['usd'],
                    'market_cap': current_data['bitcoin']['usd_market_cap'],
                    'vol_24h': current_data['bitcoin']['usd_24h_vol'],
                    'change_24h': current_data['bitcoin']['usd_24h_change'],
                    'timestamp': datetime.now().isoformat()
                }
                print(f"  ✓ Current Bitcoin price: ${current_price['price']:,.2f}")
                
                # Ensure data directory exists
                os.makedirs('data', exist_ok=True)
                
                # Save current price data for dashboard
                with open('data/current_price.json', 'w') as f:
                    json.dump(current_price, f)
                return current_price
        else:
            print(f"  ⚠️ Could not fetch current price: {current_response.status_code}")
    except Exception as e:
        print(f"  ⚠️ Error fetching current price: {str(e)}")
    return None

def fetch_bitcoin_prices(days=30, interval='daily', source='coingecko'):
    """
    Fetch Bitcoin price data from an API source.
    
    Args:
        days (int): Number of days of historical data to fetch
        interval (str): Time interval ('daily', 'hourly')
        source (str): Data source ('coingecko', 'alternative')
        
    Returns:
        pandas.DataFrame: DataFrame with price data or None if error
    """
    try:
        # Try to get current Bitcoin price as well
        current_price = fetch_current_bitcoin_price()
        
        # Try to use cached data if it exists and is recent enough
        if os.path.exists('data/bitcoin_prices.csv'):
            try:
                df = pd.read_csv('data/bitcoin_prices.csv', encoding='utf-8-sig')
                # Check if data is recent
                if 'date' in df.columns:
                    # Convert to datetime if stored as string
                    if df['date'].dtype == 'object':
                        df['date'] = pd.to_datetime(df['date'])
                    
                    # Check if the most recent date is within 1 day
                    most_recent = df['date'].max()
                    if isinstance(most_recent, str):
                        most_recent = pd.to_datetime(most_recent)
                    
                    if datetime.now() - pd.to_datetime(most_recent) < timedelta(days=1):
                        print(f"  ✓ Using cached price data (last updated: {most_recent})")
                        return df
                print("  → Cached data found but outdated, fetching fresh data...")
            except Exception as e:
                print(f"  → Error reading cached data: {str(e)}")
                print("  → Fetching fresh data...")
        else:
            print("  → No cached data found, fetching fresh data...")
        
        # Calculate timestamps
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Convert to Unix timestamps (milliseconds)
        start_timestamp = int(start_date.timestamp() * 1000)
        end_timestamp = int(end_date.timestamp() * 1000)
        
        print(f"\ud83d\udcb0 Fetching Bitcoin price data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
        
        # Try fetching from primary API (CoinGecko)
        success = False
        for attempt in range(3):
            try:
                # Construct API URL
                url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range"
                params = {
                    'vs_currency': 'usd',
                    'from': start_timestamp // 1000,  # Convert to seconds
                    'to': end_timestamp // 1000
                }
                
                # Make API request
                print(f"  → Attempt {attempt+1}/3: Requesting data from CoinGecko...")
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                success = True
                print(f"  ✓ Successfully received data from CoinGecko API")
                break  # Break out of retry loop if successful
                
            except requests.exceptions.RequestException as e:
                # Handle rate limiting or server errors
                if "429" in str(e) or "Too Many Requests" in str(e):
                    print(f"  ⚠️ Rate limit exceeded on attempt {attempt+1}. {'Retrying...' if attempt < 2 else 'Switching to alternative source...'}")
                elif "5" in str(e)[:3]:  # 5xx server error
                    print(f"  ⚠️ Server error on attempt {attempt+1}. {'Retrying...' if attempt < 2 else 'Switching to alternative source...'}")
                else:
                    print(f"  ⚠️ API request failed on attempt {attempt+1}: {str(e)}")
                
                if attempt < 2:
                    time.sleep(1 * (attempt + 1))  # Exponential backoff
                else:
                    # All attempts failed, try alternative source
                    print("  → Attempting to use alternative price data source...")
        
        # If primary API failed, try alternate method
        if not success:
            return fetch_price_data_alternative(days, interval)
            
        # Process price data
        if 'prices' not in data or not data['prices']:
            print("\u274c Empty price data received from API")
            return fetch_price_data_alternative(days, interval)
            
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
        try:
            prices_df.to_csv('data/bitcoin_prices.csv', index=False, encoding='utf-8')
            print(f"\u2705 Successfully fetched {len(prices_df)} price data points")
        except UnicodeEncodeError:
            # Handle Unicode encoding issues
            print("\u26a0\ufe0f Unicode encoding issues detected. Trying alternative encoding...")
            try:
                # Replace problematic Unicode characters
                for col in prices_df.select_dtypes(include=['object']).columns:
                    prices_df[col] = prices_df[col].astype(str).apply(lambda x: x.encode('ascii', 'replace').decode('ascii'))
                prices_df.to_csv('data/bitcoin_prices.csv', index=False, encoding='ascii')
                print(f"\u2705 Successfully saved price data with alternative encoding")
            except Exception as e3:
                print(f"\u26a0\ufe0f Error saving with alternative encoding: {str(e3)}")
                # Try a simpler approach as last resort
                try:
                    prices_df.to_csv('data/bitcoin_prices.csv', index=False, encoding='ascii', errors='replace')
                    print(f"\u2705 Saved price data with encoding error replacement")
                except Exception as e4:
                    print(f"\u274c Could not save price data: {str(e4)}")
        
        # Print price range statistics
        min_price = prices_df['price'].min()
        max_price = prices_df['price'].max()
        avg_price = prices_df['price'].mean()
        print(f"\ud83d\udcca Price range: ${min_price:.2f} - ${max_price:.2f} (avg: ${avg_price:.2f})")
        
        return prices_df
        
    except Exception as e:
        print(f"\u274c Error processing price data: {str(e)}")
        return fetch_price_data_alternative(days, interval)

def fetch_price_data_alternative(days, interval='daily'):
    """
    Alternative method to get Bitcoin price data when the primary API fails.
    Generates synthetic data based on realistic price movements if no actual data is available.
    
    Args:
        days (int): Number of days of data to generate
        interval (str): Data interval ('daily' or 'hourly')
        
    Returns:
        pandas.DataFrame: DataFrame with price data (real or synthetic)
    """
    try:
        # Try to use older cached data if available
        if os.path.exists('data/bitcoin_prices.csv'):
            print("  → Using cached price data from previous runs...")
            cached_df = pd.read_csv('data/bitcoin_prices.csv')
            if len(cached_df) > 0:
                print(f"  ✓ Found {len(cached_df)} cached price data points")
                return cached_df
                
        # Generate synthetic data based on realistic Bitcoin behavior
        print("  → Generating synthetic price data for demonstration...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Determine time points based on interval
        if interval == 'hourly':
            date_range = pd.date_range(start=start_date, end=end_date, freq='H')
        else:  # daily
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')
            
        # Start with a realistic Bitcoin price
        base_price = 50000
        
        # Generate realistic Bitcoin price movements with volatility
        import numpy as np
        # Use a random seed for reproducibility, but allow for some randomness
        np.random.seed(int(time.time()) % 1000)  
        
        # Parameters to create realistic price movements
        trend = 0.001  # Slight upward trend
        volatility = 0.02  # 2% daily volatility
        prices = [base_price]
        
        for i in range(1, len(date_range)):
            # Random walk with drift and occasional jumps
            change = prices[-1] * (trend + volatility * np.random.randn())
            # Add occasional large moves (5% chance of ±5-10% move)
            if np.random.random() < 0.05:  
                change += prices[-1] * (0.05 + 0.05 * np.random.random()) * (1 if np.random.random() > 0.5 else -1)
            new_price = max(1000, prices[-1] + change)  # Ensure price doesn't go too low
            prices.append(new_price)
            
        # Create DataFrame
        synthetic_df = pd.DataFrame({
            'timestamp': date_range,
            'price': prices,
            'date': date_range.date,
            'hour': date_range.hour if interval == 'hourly' else 0
        })
        
        # Save synthetic data
        os.makedirs('data', exist_ok=True)
        synthetic_df.to_csv('data/bitcoin_prices.csv', index=False)
        print(f"\u2705 Generated {len(synthetic_df)} synthetic price data points for demonstration")
        
        return synthetic_df
            
    except Exception as e:
        print(f"\u274c Error generating alternative price data: {str(e)}")
        # Create minimal synthetic data as a last resort
        dates = pd.date_range(start=datetime.now() - timedelta(days=days), periods=days)
        df = pd.DataFrame({
            'timestamp': dates,
            'price': [50000 + i * 100 for i in range(days)],  # Simple increasing price
            'date': [d.date() for d in dates],
            'hour': 0
        })
        return df

if __name__ == "__main__":
    # Test the function
    print("TESTING BITCOIN PRICE DATA FETCHING")
    print("=" * 50)
    
    days = int(input("How many days of price data to fetch (1-30): ") or "7")
    interval = input("Interval ('daily' or 'hourly'): ") or "daily"
    
    if interval not in ['daily', 'hourly']:
        print("Invalid interval, using 'daily'")
        interval = 'daily'
        
    fetch_bitcoin_prices(days=days, interval=interval)
