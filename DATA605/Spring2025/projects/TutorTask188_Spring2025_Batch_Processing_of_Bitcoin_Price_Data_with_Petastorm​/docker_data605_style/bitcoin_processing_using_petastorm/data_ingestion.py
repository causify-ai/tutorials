# data_ingestion.py
import requests
import time
import pandas as pd
from datetime import datetime
import os

class BitcoinDataCollector:
    def __init__(self, output_dir='bitcoin_data'):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.historical_data = []
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
    def fetch_current_price(self):
        """Fetch current Bitcoin price in USD"""
        endpoint = f"{self.base_url}/simple/price"
        params = {
            'ids': 'bitcoin',
            'vs_currencies': 'usd',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true'
        }
        response = requests.get(endpoint, params=params)
        data = response.json()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'price_usd': data['bitcoin']['usd'],
            'market_cap': data['bitcoin']['usd_market_cap'],
            'volume_24h': data['bitcoin']['usd_24h_vol'],
            'price_change_24h': data['bitcoin']['usd_24h_change']
        }
    
    def save_to_csv(self, df, filename=None):
        """Save DataFrame to CSV file"""
        if filename is None:
            filename = f"bitcoin_prices_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        filepath = os.path.join(self.output_dir, filename)
        df.to_csv(filepath, index=False)
        print(f"Data saved to {filepath}")
        return filepath
    
    def collect_data(self, interval=3600, duration=24, save_interval=24):
        """
        Collect data at regular intervals for a specified duration
        
        Args:
            interval: seconds between data fetches (default: 3600 = 1 hour)
            duration: hours to collect data (default: 24 hours)
            save_interval: save to CSV every X fetches (default: 24)
        """
        end_time = time.time() + duration * 3600
        fetch_count = 0
        
        while time.time() < end_time:
            try:
                price_data = self.fetch_current_price()
                self.historical_data.append(price_data)
                fetch_count += 1
                print(f"Collected data at {price_data['timestamp']}")
                
                # Save to CSV at specified intervals
                if fetch_count % save_interval == 0:
                    df = pd.DataFrame(self.historical_data)
                    self.save_to_csv(df)
                
            except Exception as e:
                print(f"Error fetching data: {e}")
            
            time.sleep(interval)
        
        # Save final data
        df = pd.DataFrame(self.historical_data)
        csv_path = self.save_to_csv(df, "bitcoin_prices_final.csv")
        return df, csv_path

def test_data_ingestion():
    """Test function for data ingestion module"""
    print("=== Testing Data Ingestion ===")
    collector = BitcoinDataCollector(output_dir='test_bitcoin_data')
    
    # Test single price fetch
    print("\nTesting single price fetch:")
    price_data = collector.fetch_current_price()
    print("Current Bitcoin Price Data:")
    for key, value in price_data.items():
        print(f"{key}: {value}")
    
    # Test data collection (short version - 2 minutes with 10-second intervals)
    print("\nTesting data collection (10 minutes with 30-second intervals):")
    test_df, csv_path = collector.collect_data(
        interval=30, 
        duration=10/60,  # 2 minutes
        save_interval=2  # Save every 2 fetches
    )
    
    print("\nCollected Data Sample:")
    print(test_df.head())
    
    print("\nCSV File Created:")
    print(csv_path)
    
    return test_df, csv_path

if __name__ == "__main__":
    test_data_ingestion()