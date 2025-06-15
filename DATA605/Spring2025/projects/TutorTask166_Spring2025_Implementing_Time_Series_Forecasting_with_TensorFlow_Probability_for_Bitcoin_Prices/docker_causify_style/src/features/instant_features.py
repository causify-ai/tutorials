import numpy as np
import pandas as pd
from typing import Optional

class InstantFeatureExtractor:
    def __init__(self, config):
        self.config = config

    def transform(self, series: np.ndarray) -> np.ndarray:
        """Transform the input series into features."""
        if series is None or len(series) < 2:
            return None
            
        # For now, we'll just use the raw values
        # You can add more feature engineering here if needed
        return series

    def inverse_transform(self, series: np.ndarray) -> np.ndarray:
        """Inverse transform the features back to original scale."""
        # For now, just return the values as is
        return series 