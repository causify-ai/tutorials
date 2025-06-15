import pandas as pd

class FeatureEngineer:
    def __init__(self, target_col="price", n_lags=3, roll_windows=[6, 24]):
        """
        Initializes the feature engineering configuration.
        
        Args:
            target_col (str): Column to forecast (default = "price")
            n_lags (int): Number of lag features to generate
            roll_windows (list): Window sizes for rolling statistics
        """
        self.target_col = target_col
        self.n_lags = n_lags
        self.roll_windows = roll_windows

    def transform(self, df):
        """
        Transforms the input DataFrame into supervised learning format
        with lag features, rolling statistics, and a target column.

        Args:
            df (pd.DataFrame): DataFrame with 'timestamp', 'price', 'volume', 'market_cap'

        Returns:
            pd.DataFrame: Transformed DataFrame ready for modeling
        """
        df = df.sort_values("timestamp").reset_index(drop=True)

        # Lag features
        for lag in range(1, self.n_lags + 1):
            df[f"{self.target_col}_lag_{lag}"] = df[self.target_col].shift(lag)
            df[f"volume_lag_{lag}"] = df["volume"].shift(lag)
            df[f"market_cap_lag_{lag}"] = df["market_cap"].shift(lag)

        # Rolling statistics
        for window in self.roll_windows:
            df[f"{self.target_col}_roll_mean_{window}"] = df[self.target_col].rolling(window).mean()
            df[f"{self.target_col}_roll_std_{window}"] = df[self.target_col].rolling(window).std()

        # Target: next time-step price
        df["target"] = df[self.target_col].shift(-1)

        # Drop rows with NaNs
        df = df.dropna().reset_index(drop=True)
        return df
