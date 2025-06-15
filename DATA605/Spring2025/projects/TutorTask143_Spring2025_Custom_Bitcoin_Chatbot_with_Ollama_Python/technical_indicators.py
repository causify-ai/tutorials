"""
Technical indicators module for cryptocurrency analysis.
Implements common technical indicators like RSI, MACD, etc.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Union, Tuple, Any

logger = logging.getLogger(__name__)

class TechnicalIndicators:
    """Implements technical indicators for cryptocurrency analysis."""
    
    @staticmethod
    def calculate_rsi(data: pd.DataFrame, period: int = 14, price_col: str = 'price') -> pd.DataFrame:
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            data: DataFrame with price data
            period: RSI period (typically 14)
            price_col: Column name containing price data
            
        Returns:
            DataFrame with RSI values added
        """
        if len(data) < period + 1:
            logger.warning(f"Not enough data to calculate RSI (need {period+1}, got {len(data)})")
            return data
            
        # Make a copy to avoid modifying the original
        df = data.copy()
        
        # Calculate price changes
        df['price_change'] = df[price_col].diff()
        
        # Calculate gains and losses
        df['gain'] = df['price_change'].apply(lambda x: x if x > 0 else 0)
        df['loss'] = df['price_change'].apply(lambda x: abs(x) if x < 0 else 0)
        
        # Calculate average gains and losses
        df['avg_gain'] = df['gain'].rolling(window=period).mean()
        df['avg_loss'] = df['loss'].rolling(window=period).mean()
        
        # Calculate RS and RSI
        df['rs'] = df['avg_gain'] / df['avg_loss']
        df['rsi'] = 100 - (100 / (1 + df['rs']))
        
        # Clean up intermediate columns
        df = df.drop(['price_change', 'gain', 'loss', 'avg_gain', 'avg_loss', 'rs'], axis=1)
        
        return df
    
    @staticmethod
    def calculate_macd(data: pd.DataFrame, fast_period: int = 12, slow_period: int = 26, 
                       signal_period: int = 9, price_col: str = 'price') -> pd.DataFrame:
        """
        Calculate Moving Average Convergence Divergence (MACD).
        
        Args:
            data: DataFrame with price data
            fast_period: Fast EMA period (typically 12)
            slow_period: Slow EMA period (typically 26)
            signal_period: Signal line period (typically 9)
            price_col: Column name containing price data
            
        Returns:
            DataFrame with MACD values added
        """
        if len(data) < slow_period + signal_period:
            logger.warning(f"Not enough data to calculate MACD (need {slow_period+signal_period}, got {len(data)})")
            return data
            
        # Make a copy to avoid modifying the original
        df = data.copy()
        
        # Calculate EMAs
        df['ema_fast'] = df[price_col].ewm(span=fast_period, adjust=False).mean()
        df['ema_slow'] = df[price_col].ewm(span=slow_period, adjust=False).mean()
        
        # Calculate MACD line and signal line
        df['macd_line'] = df['ema_fast'] - df['ema_slow']
        df['macd_signal'] = df['macd_line'].ewm(span=signal_period, adjust=False).mean()
        
        # Calculate MACD histogram
        df['macd_histogram'] = df['macd_line'] - df['macd_signal']
        
        # Clean up intermediate columns
        df = df.drop(['ema_fast', 'ema_slow'], axis=1)
        
        return df
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.DataFrame, period: int = 20, 
                                 std_dev: float = 2.0, price_col: str = 'price') -> pd.DataFrame:
        """
        Calculate Bollinger Bands.
        
        Args:
            data: DataFrame with price data
            period: Moving average period (typically 20)
            std_dev: Number of standard deviations (typically 2)
            price_col: Column name containing price data
            
        Returns:
            DataFrame with Bollinger Bands values added
        """
        if len(data) < period:
            logger.warning(f"Not enough data to calculate Bollinger Bands (need {period}, got {len(data)})")
            return data
            
        # Make a copy to avoid modifying the original
        df = data.copy()
        
        # Calculate middle band (SMA)
        df['bb_middle'] = df[price_col].rolling(window=period).mean()
        
        # Calculate standard deviation
        df['bb_std'] = df[price_col].rolling(window=period).std()
        
        # Calculate upper and lower bands
        df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * std_dev)
        df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * std_dev)
        
        # Clean up intermediate columns
        df = df.drop(['bb_std'], axis=1)
        
        return df
    
    @staticmethod
    def generate_signals(data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on technical indicators."""
        df = data.copy()
        
        # Initialize signals column
        df['signal'] = 'hold'
        
        # RSI signals
        if 'rsi' in df.columns:
            # Ensure RSI values are numeric
            df['rsi'] = pd.to_numeric(df['rsi'], errors='coerce')
            
            # Create the column with appropriate dtype first
            df['rsi_signal'] = pd.Series(dtype='object')
            
            # Now apply the conditions
            df.loc[df['rsi'] < 30, 'rsi_signal'] = 'buy'
            df.loc[df['rsi'] > 70, 'rsi_signal'] = 'sell'
            df.loc[(df['rsi'] >= 30) & (df['rsi'] <= 70), 'rsi_signal'] = 'hold'
        
        # MACD signals
        if all(col in df.columns for col in ['macd_line', 'macd_signal']):
            # Ensure MACD values are numeric
            df['macd_line'] = pd.to_numeric(df['macd_line'], errors='coerce')
            df['macd_signal'] = pd.to_numeric(df['macd_signal'], errors='coerce')
            
            # Create macd_cross column with object dtype
            df['macd_cross'] = pd.Series(dtype='object')
            
            # MACD line crosses above signal line
            mask = (df['macd_line'] > df['macd_signal']) & (df['macd_line'].shift(1) <= df['macd_signal'].shift(1))
            df.loc[mask, 'macd_cross'] = 'bullish'
            
            # MACD line crosses below signal line
            mask = (df['macd_line'] < df['macd_signal']) & (df['macd_line'].shift(1) >= df['macd_signal'].shift(1))
            df.loc[mask, 'macd_cross'] = 'bearish'
            
            # Fill NaN values with previous value
            df['macd_cross'] = df['macd_cross'].ffill()
            
            # Create macd_signal column with appropriate dtype
            df['macd_signal_indicator'] = pd.Series(dtype='object')
            
            # Generate MACD signals
            df.loc[df['macd_cross'] == 'bullish', 'macd_signal_indicator'] = 'buy'
            df.loc[df['macd_cross'] == 'bearish', 'macd_signal_indicator'] = 'sell'
            df['macd_signal_indicator'] = df['macd_signal_indicator'].fillna('hold')
            
            # Rename to avoid confusion with the original macd_signal column
            if 'macd_signal_indicator' in df.columns:
                df.rename(columns={'macd_signal_indicator': 'macd_signal_action'}, inplace=True)
        
        # Combined signal (RSI and MACD)
        if 'rsi_signal' in df.columns and 'macd_signal_action' in df.columns:
            # Strong buy: Both RSI and MACD suggest buying
            df.loc[(df['rsi_signal'] == 'buy') & (df['macd_signal_action'] == 'buy'), 'signal'] = 'strong_buy'
            
            # Strong sell: Both RSI and MACD suggest selling
            df.loc[(df['rsi_signal'] == 'sell') & (df['macd_signal_action'] == 'sell'), 'signal'] = 'strong_sell'
            
            # Weak buy: Either RSI or MACD suggests buying
            mask1 = (df['rsi_signal'] == 'buy') & (df['macd_signal_action'] != 'sell')
            mask2 = (df['macd_signal_action'] == 'buy') & (df['rsi_signal'] != 'sell')
            df.loc[mask1 | mask2, 'signal'] = 'buy'
            
            # Weak sell: Either RSI or MACD suggests selling
            mask1 = (df['rsi_signal'] == 'sell') & (df['macd_signal_action'] != 'buy')
            mask2 = (df['macd_signal_action'] == 'sell') & (df['rsi_signal'] != 'buy')
            df.loc[mask1 | mask2, 'signal'] = 'sell'
        
        return df
    
    @staticmethod
    def analyze_historical_data(data: pd.DataFrame, price_col: str = 'price') -> Dict[str, Any]:
        """
        Perform comprehensive technical analysis on historical data.
        
        Args:
            data: DataFrame with price data
            price_col: Column name containing price data
            
        Returns:
            Dictionary with technical analysis results
        """
        if len(data) < 50:  # Need sufficient data for meaningful analysis
            return {"error": "Insufficient data for technical analysis"}
            
        # Make a copy to avoid modifying the original
        df = data.copy()
        
        # Calculate all indicators
        df = TechnicalIndicators.calculate_rsi(df, price_col=price_col)
        df = TechnicalIndicators.calculate_macd(df, price_col=price_col)
        df = TechnicalIndicators.calculate_bollinger_bands(df, price_col=price_col)
        
        # Generate signals
        df = TechnicalIndicators.generate_signals(df)
        
        # Get current values (most recent data point)
        current = df.iloc[-1].to_dict()
        
        # Determine current market condition
        market_condition = "neutral"
        if current.get('rsi', 50) < 30:
            market_condition = "oversold"
        elif current.get('rsi', 50) > 70:
            market_condition = "overbought"
            
        # Determine trend based on MACD
        trend = "sideways"
        if 'macd_line' in current and 'macd_signal' in current:
            if current['macd_line'] > current['macd_signal'] and current['macd_line'] > 0:
                trend = "bullish"
            elif current['macd_line'] < current['macd_signal'] and current['macd_line'] < 0:
                trend = "bearish"
        
        # Check if price is near Bollinger Bands
        volatility_condition = "normal"
        if 'bb_upper' in current and 'bb_lower' in current and price_col in current:
            price = current[price_col]
            upper = current['bb_upper']
            lower = current['bb_lower']
            
            if price > upper * 0.95:  # Within 5% of upper band
                volatility_condition = "high_volatility_upper"
            elif price < lower * 1.05:  # Within 5% of lower band
                volatility_condition = "high_volatility_lower"
        
        # Prepare analysis summary
        analysis = {
            "timestamp": df.index[-1] if isinstance(df.index, pd.DatetimeIndex) else None,
            "price": current.get(price_col),
            "rsi": current.get('rsi'),
            "macd_line": current.get('macd_line'),
            "macd_signal": current.get('macd_signal'),
            "macd_histogram": current.get('macd_histogram'),
            "bollinger_middle": current.get('bb_middle'),
            "bollinger_upper": current.get('bb_upper'),
            "bollinger_lower": current.get('bb_lower'),
            "market_condition": market_condition,
            "trend": trend,
            "volatility": volatility_condition,
            "signal": current.get('signal', 'hold'),
            "analysis_date": pd.Timestamp.now().isoformat()
        }
        
        return analysis