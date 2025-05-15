"""
Technical analysis and time series utility functions for Bitcoin price forecasting.
"""

import pandas as pd
import numpy as np
from typing import Union, Tuple, List, Dict, Any
from datetime import datetime, timedelta

def calculate_moving_averages(data: pd.Series, windows: List[int] = [5, 10, 20, 50]) -> pd.DataFrame:
    """
    Calculate simple and exponential moving averages for multiple timeframes.

    :param data: Price time series data
    :param windows: List of window sizes for moving averages
    :return: DataFrame with SMA and EMA columns
    """
    df = pd.DataFrame()
    for window in windows:
        df[f'sma_{window}'] = data.rolling(window=window).mean()
        df[f'ema_{window}'] = data.ewm(span=window).mean()
    return df

def calculate_bollinger_bands(data: pd.Series, window: int = 20, num_std: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate Bollinger Bands for price data.

    :param data: Price time series data
    :param window: Window size for moving average
    :param num_std: Number of standard deviations for bands
    :return: Tuple of (middle band, upper band, lower band)
    """
    middle_band = data.rolling(window=window).mean()
    std = data.rolling(window=window).std()
    upper_band = middle_band + (std * num_std)
    lower_band = middle_band - (std * num_std)
    return middle_band, upper_band, lower_band

def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).

    :param data: Price time series data
    :param period: RSI period
    :return: RSI values
    """
    delta = data.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.finfo(float).eps)
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data: pd.Series, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate MACD (Moving Average Convergence Divergence).

    :param data: Price time series data
    :param fast_period: Fast EMA period
    :param slow_period: Slow EMA period
    :param signal_period: Signal line period
    :return: Tuple of (MACD line, signal line, histogram)
    """
    fast_ema = data.ewm(span=fast_period).mean()
    slow_ema = data.ewm(span=slow_period).mean()
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal_period).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def calculate_volatility(data: pd.Series, windows: List[int] = [10, 20, 50]) -> Dict[str, pd.Series]:
    """
    Calculate various volatility measures.

    :param data: Price time series data
    :param windows: List of window sizes for volatility calculation
    :return: Dictionary of volatility measures
    """
    volatility = {}
    for window in windows:
        # Standard deviation based volatility
        volatility[f'std_{window}'] = data.rolling(window=window).std()
        # Log returns volatility
        log_returns = np.log(data / data.shift(1))
        volatility[f'log_vol_{window}'] = log_returns.rolling(window=window).std() * np.sqrt(252)  # Annualized
    return volatility

def detect_outliers(data: pd.Series, method: str = 'iqr', threshold: float = 1.5) -> Tuple[pd.Series, List[int]]:
    """
    Detect outliers in price data using various methods.

    :param data: Price time series data
    :param method: Method to use ('iqr' or 'zscore')
    :param threshold: Threshold for outlier detection
    :return: Tuple of (cleaned data, outlier indices)
    """
    if method == 'iqr':
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        outliers = (data < lower_bound) | (data > upper_bound)
    else:  # zscore
        z_scores = (data - data.mean()) / data.std()
        outliers = abs(z_scores) > threshold
    
    outlier_indices = list(outliers[outliers].index)
    cleaned_data = data.copy()
    if len(outlier_indices) > 0:
        for idx in outlier_indices:
            # Use exponential weighted average for replacement
            start_idx = max(0, idx - 10)
            end_idx = min(len(data), idx + 11)
            local_values = data[start_idx:end_idx].copy()
            if idx in local_values.index:
                local_values = local_values.drop(idx)
            if not local_values.empty:
                cleaned_data[idx] = local_values.ewm(span=5).mean().iloc[-1]
    
    return cleaned_data, outlier_indices

def calculate_trend(data: pd.Series, windows: List[int] = [3, 5, 10]) -> Dict[str, float]:
    """
    Calculate price trends over multiple timeframes.

    :param data: Price time series data
    :param windows: List of window sizes for trend calculation
    :return: Dictionary of trend metrics
    """
    trends = {}
    for window in windows:
        if len(data) >= window:
            window_data = data[-window:]
            x = np.arange(len(window_data))
            slope, intercept = np.polyfit(x, window_data, 1)
            trends[f'slope_{window}'] = slope
            trends[f'r2_{window}'] = np.corrcoef(x, window_data)[0, 1] ** 2
    return trends

def preprocess_price_data(data: pd.Series, 
                         calc_ma: bool = True,
                         calc_bb: bool = True,
                         calc_rsi: bool = True,
                         calc_macd: bool = True,
                         calc_vol: bool = True) -> pd.DataFrame:
    """
    Comprehensive preprocessing of price data with technical indicators.

    :param data: Price time series data
    :param calc_ma: Whether to calculate moving averages
    :param calc_bb: Whether to calculate Bollinger Bands
    :param calc_rsi: Whether to calculate RSI
    :param calc_macd: Whether to calculate MACD
    :param calc_vol: Whether to calculate volatility metrics
    :return: DataFrame with all calculated indicators
    """
    df = pd.DataFrame({'price': data})
    
    # Clean outliers
    cleaned_data, _ = detect_outliers(data)
    df['price_cleaned'] = cleaned_data
    
    if calc_ma:
        ma_df = calculate_moving_averages(cleaned_data)
        df = pd.concat([df, ma_df], axis=1)
    
    if calc_bb:
        mid, upper, lower = calculate_bollinger_bands(cleaned_data)
        df['bb_middle'] = mid
        df['bb_upper'] = upper
        df['bb_lower'] = lower
    
    if calc_rsi:
        for period in [6, 14, 28]:
            df[f'rsi_{period}'] = calculate_rsi(cleaned_data, period)
    
    if calc_macd:
        for (fast, slow) in [(12, 26), (5, 35)]:
            macd, signal, hist = calculate_macd(cleaned_data, fast, slow)
            df[f'macd_{fast}_{slow}'] = macd
            df[f'macd_signal_{fast}_{slow}'] = signal
            df[f'macd_hist_{fast}_{slow}'] = hist
    
    if calc_vol:
        volatility = calculate_volatility(cleaned_data)
        for key, value in volatility.items():
            df[f'vol_{key}'] = value
    
    # Calculate trends
    trends = calculate_trend(cleaned_data)
    for key, value in trends.items():
        df[f'trend_{key}'] = value
    
    return df

def normalize_features(df: pd.DataFrame, exclude_cols: List[str] = ['price']) -> pd.DataFrame:
    """
    Normalize all features to similar scale.

    :param df: DataFrame with features
    :param exclude_cols: Columns to exclude from normalization
    :return: DataFrame with normalized features
    """
    normalized = df.copy()
    for col in df.columns:
        if col not in exclude_cols:
            normalized[col] = (df[col] - df[col].mean()) / (df[col].std() + 1e-8)
    return normalized 

def detect_price_shocks(data: pd.Series, window: int = 5, threshold: float = 0.02) -> List[int]:
    """
    Detect sudden price shocks (significant price changes).
    
    :param data: Price time series data
    :param window: Window size for rolling calculation
    :param threshold: Threshold for shock detection (as percentage)
    :return: List of indices where shocks were detected
    """
    pct_changes = data.pct_change().abs()
    shock_indices = list(pct_changes[pct_changes > threshold].index)
    return shock_indices

def calculate_adaptive_forecast(data: pd.Series, 
                               lookback_windows: List[int] = [3, 5, 10],
                               volatility_scaling: bool = True) -> Dict[str, float]:
    """
    Calculate forecast using adaptive weighting based on market conditions.
    
    :param data: Price time series data
    :param lookback_windows: List of window sizes for trend calculation
    :param volatility_scaling: Whether to scale adjustments by volatility
    :return: Dictionary with forecast values and adjustments
    """
    if len(data) < max(lookback_windows):
        return {'forecast': data.iloc[-1], 'adjustments': {}}
    
    last_price = data.iloc[-1]
    result = {'forecast': last_price, 'adjustments': {}}
    
    # Calculate volatility
    volatility = data.pct_change().std() if len(data) > 1 else 0.005
    
    # Calculate momentum signals
    momentum_signals = []
    for window in lookback_windows:
        if len(data) >= window + 1:
            # Rate of change
            roc = (last_price / data.iloc[-window] - 1) * 100
            momentum_signals.append(roc)
    
    # Calculate moving averages
    ma_signals = []
    for window in [5, 10, 20]:
        if len(data) >= window:
            ma = data.rolling(window=window).mean().iloc[-1]
            # Calculate position relative to MA
            ma_signals.append((last_price / ma - 1) * 100)
    
    # Calculate RSI
    rsi = None
    if len(data) >= 14:
        delta = data.diff()
        gain = delta.clip(lower=0).rolling(window=14).mean()
        loss = -delta.clip(upper=0).rolling(window=14).mean()
        rs = gain / loss.replace(0, np.finfo(float).eps)
        rsi = 100 - (100 / (1 + rs)).iloc[-1]
    
    # Apply momentum adjustment
    if momentum_signals:
        # Weight recent momentum more heavily
        weights = np.array([0.5, 0.3, 0.2][:len(momentum_signals)])
        weights = weights / weights.sum()
        weighted_momentum = np.sum(np.array(momentum_signals) * weights)
        
        # Scale factor based on volatility if requested
        if volatility_scaling:
            momentum_factor = min(0.5, max(0.1, 0.3 * (1 - volatility * 20)))
        else:
            momentum_factor = 0.3
            
        momentum_adjustment = last_price * (weighted_momentum / 100) * momentum_factor
        result['forecast'] += momentum_adjustment
        result['adjustments']['momentum'] = momentum_adjustment
    
    # Apply MA adjustment
    if ma_signals:
        avg_ma_signal = np.mean(ma_signals)
        ma_adjustment = 0
        
        if abs(avg_ma_signal) > 1.0:  # >1% away from MAs
            if volatility_scaling and volatility > 0.01:
                # Mean reversion in high volatility
                ma_adjustment = -last_price * (avg_ma_signal / 100) * 0.2
            else:
                # Trend following in low volatility
                ma_adjustment = last_price * (avg_ma_signal / 100) * 0.1
                
        if ma_adjustment != 0:
            result['forecast'] += ma_adjustment
            result['adjustments']['moving_average'] = ma_adjustment
    
    # Apply RSI adjustment
    if rsi is not None:
        rsi_adjustment = 0
        
        if rsi < 30:
            # Oversold - expect upward correction
            rsi_strength = (30 - rsi) / 30
            rsi_adjustment = last_price * 0.002 * rsi_strength
        elif rsi > 70:
            # Overbought - expect downward correction
            rsi_strength = (rsi - 70) / 30
            rsi_adjustment = -last_price * 0.002 * rsi_strength
            
        if rsi_adjustment != 0:
            result['forecast'] += rsi_adjustment
            result['adjustments']['rsi'] = rsi_adjustment
    
    # Recent change adjustment
    if len(data) >= 2:
        price_change = last_price - data.iloc[-2]
        if abs(price_change) > last_price * 0.005:  # >0.5% change
            # Weight more in trending markets
            if len(momentum_signals) > 0 and momentum_signals[0] * price_change > 0:
                change_weight = 0.3  # Same direction as trend
            else:
                change_weight = 0.1  # Possible reversal or noise
                
            recent_change_adjustment = price_change * change_weight
            result['forecast'] += recent_change_adjustment
            result['adjustments']['recent_change'] = recent_change_adjustment
    
    # Round forecast
    result['forecast'] = round(result['forecast'], 2)
    
    return result

def calculate_confidence_interval(data: pd.Series, 
                                 forecast: float, 
                                 confidence: float = 0.95,
                                 volatility_scaling: bool = True) -> Tuple[float, float]:
    """
    Calculate confidence interval for a forecast based on recent volatility.
    
    :param data: Price time series data
    :param forecast: Forecast value
    :param confidence: Confidence level (default: 0.95 for 95% CI)
    :param volatility_scaling: Whether to scale interval by recent volatility
    :return: Tuple of (lower bound, upper bound)
    """
    if len(data) < 5:
        # Default confidence interval of ±0.5%
        std = forecast * 0.005
    else:
        # Calculate standard deviation from recent data
        std = data.tail(10).std()
    
    # Z-score for the given confidence level
    # 1.96 for 95% confidence
    z_score = 1.96
    if confidence != 0.95:
        # Calculate z-score for other confidence levels
        from scipy import stats
        z_score = stats.norm.ppf(1 - (1 - confidence) / 2)
    
    # Base interval
    interval = z_score * std
    
    # Adjust for volatility if requested
    if volatility_scaling and len(data) > 1:
        volatility = data.pct_change().std()
        vol_factor = 1.0 + (volatility * 50)  # Increase interval in high volatility
        interval *= vol_factor
    
    lower_bound = forecast - interval
    upper_bound = forecast + interval
    
    return round(lower_bound, 2), round(upper_bound, 2)

def ensemble_forecast(data: pd.Series, 
                     methods: List[str] = ['tfp', 'technical', 'arima', 'ewm'],
                     weights: List[float] = None) -> Dict[str, Any]:
    """
    Generate ensemble forecast combining multiple forecasting methods.
    
    :param data: Price time series data
    :param methods: List of forecasting methods to include
    :param weights: List of weights for each method (must sum to 1)
    :return: Dictionary with ensemble forecast and components
    """
    if len(data) < 10:
        return {'forecast': data.iloc[-1], 'lower': data.iloc[-1] * 0.995, 'upper': data.iloc[-1] * 1.005}
    
    forecasts = {}
    
    # Default to equal weights if not provided
    if weights is None:
        weights = [1.0 / len(methods)] * len(methods)
    
    # Ensure weights sum to 1
    weights = np.array(weights) / np.sum(weights)
    
    # Generate forecasts using different methods
    for method in methods:
        if method == 'ewm':
            # Exponential weighted moving average
            forecasts['ewm'] = data.ewm(span=3).mean().iloc[-1]
        
        elif method == 'technical':
            # Technical analysis based forecast
            tech_forecast = calculate_adaptive_forecast(data)
            forecasts['technical'] = tech_forecast['forecast']
        
        elif method == 'arima':
            try:
                # Simple ARIMA forecast
                from statsmodels.tsa.arima.model import ARIMA
                model = ARIMA(data, order=(2, 1, 0))
                model_fit = model.fit()
                forecasts['arima'] = model_fit.forecast(1)[0]
            except:
                # Fall back to EWM if ARIMA fails
                forecasts['arima'] = data.ewm(span=5).mean().iloc[-1]
        
        elif method == 'tfp':
            # Placeholder for TensorFlow Probability forecast
            # In practice, this would come from the TFP model
            forecasts['tfp'] = data.iloc[-1]
    
    # Calculate weighted ensemble forecast
    ensemble_value = 0
    for i, method in enumerate(methods):
        ensemble_value += forecasts[method] * weights[i]
    
    # Calculate confidence interval
    lower, upper = calculate_confidence_interval(data, ensemble_value)
    
    return {
        'forecast': round(ensemble_value, 2),
        'lower': lower,
        'upper': upper,
        'components': forecasts
    } 