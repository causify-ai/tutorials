import pandas as pd
import numpy as np
from .base import FeatureEngineer

class HistoryFeatureEngineer(FeatureEngineer):
    def __init__(self, config: dict):
        hist = config['history']
        self.vol_window = hist['rolling_vol']
        self.seasonal   = hist['seasonal_period']

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        # Ensure price column exists and is numeric
        if 'price' not in df.columns:
            raise ValueError("Input DataFrame must contain a 'price' column")
        
        # Convert price to numeric, handling any non-numeric values
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        
        # Calculate log returns with proper handling of missing values
        df['log_return'] = np.log(df['price'] / df['price'].shift(1))
        
        # Calculate rolling volatility with proper window handling
        df['vol_7d'] = df['log_return'].rolling(
            window=self.vol_window,
            min_periods=1  # Allow partial windows
        ).std()
        
        # Add day of week features
        df['dow'] = df.index.dayofweek
        dummies = pd.get_dummies(df['dow'], prefix='dow')
        
        # Combine features and drop any remaining NaN values
        result = pd.concat([df, dummies], axis=1)
        return result.dropna()