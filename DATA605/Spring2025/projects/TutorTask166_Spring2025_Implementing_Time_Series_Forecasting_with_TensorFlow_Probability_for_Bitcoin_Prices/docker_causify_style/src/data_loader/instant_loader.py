import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import time
from typing import Optional, Tuple

class InstantCSVLoader:
    def __init__(self, config):
        self.config = config
        self.raw_data_file = config['data']['raw_data']['instant_data']['file']
        self.window_size = timedelta(minutes=5)  # 5-minute window for predictions
        self.last_check_time = None
        self.ensure_data_file_exists()

    def ensure_data_file_exists(self):
        """Ensure the data file exists and has headers."""
        if not os.path.exists(self.raw_data_file):
            os.makedirs(os.path.dirname(self.raw_data_file), exist_ok=True)
            pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']).to_csv(
                self.raw_data_file, index=False
            )

    def load_latest_data(self) -> Optional[pd.DataFrame]:
        """Load the latest data for real-time predictions."""
        try:
            if not os.path.exists(self.raw_data_file):
                self.ensure_data_file_exists()
                return None

            # Read the CSV file
            df = pd.read_csv(self.raw_data_file)
            if len(df) == 0:
                return None

            # Convert timestamp to datetime, coerce errors
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            # Drop rows with invalid timestamps
            df = df.dropna(subset=['timestamp'])
            if len(df) == 0:
                return None

            # Get the latest timestamp
            latest_time = df['timestamp'].max()
            # Filter data to last 5 minutes
            start_time = latest_time - self.window_size
            df = df[df['timestamp'] >= start_time]
            if len(df) < 2:  # Need at least 2 points for prediction
                return None
            # Sort by timestamp
            df = df.sort_values('timestamp')
            # Extract the time series values
            series = df['close'].values
            # Store the timestamps for the model
            self.timestamps = df['timestamp'].values
            return series
        except Exception as e:
            print(f"Error loading latest data: {str(e)}")
            return None

    def fetch(self) -> pd.DataFrame:
        """Load all historical data."""
        try:
            if not os.path.exists(self.raw_data_file):
                self.ensure_data_file_exists()
                return pd.DataFrame()
            df = pd.read_csv(self.raw_data_file)
            if len(df) == 0:
                return pd.DataFrame()
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.dropna(subset=['timestamp'])
        except Exception as e:
            print(f"Error loading historical data: {str(e)}")
            return pd.DataFrame()
        return df

    def get_latest_timestamp(self) -> Optional[datetime]:
        """Get the latest timestamp from the data."""
        try:
            if not os.path.exists(self.raw_data_file):
                return None
            
            df = pd.read_csv(self.raw_data_file)
            if len(df) == 0:
                return None
                
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df['timestamp'].max()
            
        except Exception as e:
            print(f"Error getting latest timestamp: {str(e)}")
            return None

    def append_data(self, data: dict):
        """Append new data to the CSV file."""
        try:
            df = pd.DataFrame([data])
            if not os.path.exists(self.raw_data_file):
                self.ensure_data_file_exists()
            df.to_csv(self.raw_data_file, mode='a', header=False, index=False)
                
        except Exception as e:
            print(f"Error appending data: {str(e)}")