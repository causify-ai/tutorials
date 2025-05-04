import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)

def save_data(data, file_path):
    """Save data to CSV file with proper timestamp format and column names."""
    try:
        # Ensure data has all required columns
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in data:
                data[col] = data.get('price', 0)  # Use price for all columns if not available
        
        # Convert timestamp to ISO8601 format
        data['timestamp'] = pd.Timestamp(data['timestamp']).strftime('%Y-%m-%dT%H:%M:%S')
        
        # Create DataFrame with proper column order
        df = pd.DataFrame([data], columns=required_columns)
        
        # Ensure numeric columns are float64
        numeric_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Write to file with proper locking
        with open(file_path, 'a' if os.path.exists(file_path) else 'w') as f:
            # Get file lock
            import fcntl
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                # Write header if file is new
                if f.tell() == 0:
                    df.to_csv(f, index=False)
                else:
                    df.to_csv(f, mode='a', header=False, index=False)
            finally:
                # Release lock
                fcntl.flock(f, fcntl.LOCK_UN)
        
        logger.info(f"Saved data to {file_path}")
        
    except Exception as e:
        logger.error(f"Error saving data: {e}")
        raise 