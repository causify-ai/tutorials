import pandas as pd
import numpy as np
from .base import FeatureEngineer

class InstantFeatureEngineer(FeatureEngineer):
    def __init__(self, config: dict):
        inst = config['model']['instant']
        self.freq = inst['resample_freq'].replace('T', 'min')
        fw = inst['feature_windows']
        self.log_lag = fw['log_return']
        self.vol_wins = fw['vol_rolling']
        self.ma_short = fw['ma_short']
        self.ma_long  = fw['ma_long']

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Input DataFrame missing required columns: {missing_cols}")

        for col in required_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        bars = df.resample(self.freq).agg({
            'open':   'first',
            'high':   'max',
            'low':    'min',
            'close':  'last',
            'volume': 'sum'
        })

        bars['log_return'] = np.log(bars['close'] / bars['close'].shift(self.log_lag))
        for w in self.vol_wins:
            bars[f'vol_{w}min'] = bars['log_return'].rolling(
                window=w,
                min_periods=1
            ).std()
        bars['ma_short'] = bars['close'].rolling(
            window=self.ma_short,
            min_periods=1
        ).mean()
        bars['ma_long'] = bars['close'].rolling(
            window=self.ma_long,
            min_periods=1
        ).mean()

        return bars.dropna()