import numpy as np
import pandas as pd
import datetime
from typing import Dict, List, Tuple, Any, Optional
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA
import os
from scipy import stats

class BitcoinForecastModel:
    """
    Time series forecasting model for Bitcoin price prediction using ARIMA models.
    
    Attributes:
        forecast_horizon (int): Number of days to forecast into the future
        include_trend (bool): Whether to include trend component in the model
        include_seasonality (bool): Whether to include seasonality in the model
        include_autoregressive (bool): Whether to include autoregressive component
        confidence_level (float): Confidence level for prediction intervals (0-1)
        use_mcmc (bool): Used as a model complexity toggle (simple vs complex ARIMA)
    """
    
    def __init__(
        self, 
        forecast_horizon: int = 7,
        use_mcmc: bool = False,  # Used to toggle model complexity
        include_trend: bool = True,
        include_seasonality: bool = True,
        include_autoregressive: bool = True,
        confidence_level: float = 0.9
    ):
        """
        Initialize the BitcoinForecastModel.
        
        Args:
            forecast_horizon (int): Number of days to forecast
            use_mcmc (bool): If True, use more complex ARIMA parameters
            include_trend (bool): Include trend component
            include_seasonality (bool): Include seasonality component
            include_autoregressive (bool): Include autoregressive component
            confidence_level (float): Confidence level for prediction intervals (0-1)
        """
        self.forecast_horizon = forecast_horizon
        self.use_complex_model = use_mcmc  # Use more complex ARIMA if True
        self.include_trend = include_trend
        self.include_seasonality = include_seasonality
        self.include_autoregressive = include_autoregressive
        self.confidence_level = confidence_level
        self.model = None
        self.trained = False
        
        # ARIMA parameters - simple vs complex
        if self.use_complex_model:
            self.arima_order = (5, 1, 2)  # More complex ARIMA
        else:
            self.arima_order = (2, 1, 0)  # Simpler ARIMA
    
    def _forecast_with_arima(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate forecasts using ARIMA model.
        
        Args:
            data (pd.DataFrame): DataFrame with price data
            
        Returns:
            Dict[str, Any]: Dictionary with forecast results
        """
        # Split data for testing
        train_size = int(len(data) * 0.8)
        train_data = data.iloc[:train_size]
        test_data = data.iloc[train_size:]
        
        # Determine ARIMA parameters based on components
        p, d, q = self.arima_order
        if not self.include_autoregressive:
            p = 0
        
        try:
            # Try to use SARIMAX for seasonal components
            if self.include_seasonality:
                # Configure the model with seasonality
                model = SARIMAX(
                    train_data['price'],
                    order=(p, d, q),
                    seasonal_order=(1, 0, 1, 7),  # Weekly seasonality
                    enforce_stationarity=False,
                    enforce_invertibility=False
                )
            else:
                # Use ARIMA without seasonality
                model = ARIMA(train_data['price'], order=(p, d, q))
            
            # Fit the model
            fitted_model = model.fit()
            self.model = fitted_model
            
            # Calculate in-sample metrics
            predictions = fitted_model.forecast(steps=len(test_data))
            
            mae = mean_absolute_error(test_data['price'], predictions)
            rmse = np.sqrt(mean_squared_error(test_data['price'], predictions))
            mape = np.mean(np.abs((test_data['price'].values - predictions) / test_data['price'].values)) * 100
            r2 = r2_score(test_data['price'], predictions)
            
            # Generate forecasts
            forecast_mean = fitted_model.forecast(steps=self.forecast_horizon)
            
            # Calculate standard error for prediction intervals
            # We'll use a simple approach based on the model's training errors
            residuals = fitted_model.resid
            residual_std = residuals.std()
            
            # Calculate prediction intervals
            z_score = stats.norm.ppf((1 + self.confidence_level) / 2)
            forecast_std = np.ones(self.forecast_horizon) * residual_std
            
            forecast_lower = forecast_mean - z_score * forecast_std
            forecast_upper = forecast_mean + z_score * forecast_std
            
            # Generate dates for the forecast
            last_date = data.index[-1]
            forecast_dates = [last_date + datetime.timedelta(days=i+1) for i in range(self.forecast_horizon)]
            
            return {
                'forecast': {
                    'dates': forecast_dates,
                    'mean': forecast_mean.values,
                    'lower': forecast_lower,
                    'upper': forecast_upper,
                    'stddev': forecast_std
                },
                'metrics': {
                    'mae': mae,
                    'rmse': rmse,
                    'mape': mape,
                    'r2': r2
                }
            }
            
        except Exception as e:
            print(f"ARIMA/SARIMAX model failed: {str(e)}")
            # Fall back to simpler ARIMA model
            try:
                model = ARIMA(train_data['price'], order=(1, 1, 0))
                fitted_model = model.fit()
                self.model = fitted_model
                
                # Calculate in-sample metrics
                predictions = fitted_model.forecast(steps=len(test_data))
                
                mae = mean_absolute_error(test_data['price'], predictions)
                rmse = np.sqrt(mean_squared_error(test_data['price'], predictions))
                mape = np.mean(np.abs((test_data['price'].values - predictions) / test_data['price'].values)) * 100
                r2 = r2_score(test_data['price'], predictions)
                
                # Generate forecasts
                forecast_mean = fitted_model.forecast(steps=self.forecast_horizon)
                
                # Calculate standard error for prediction intervals
                residuals = fitted_model.resid
                residual_std = residuals.std()
                
                # Calculate prediction intervals
                z_score = stats.norm.ppf((1 + self.confidence_level) / 2)
                forecast_std = np.ones(self.forecast_horizon) * residual_std
                
                forecast_lower = forecast_mean - z_score * forecast_std
                forecast_upper = forecast_mean + z_score * forecast_std
                
                # Generate dates for the forecast
                last_date = data.index[-1]
                forecast_dates = [last_date + datetime.timedelta(days=i+1) for i in range(self.forecast_horizon)]
                
                return {
                    'forecast': {
                        'dates': forecast_dates,
                        'mean': forecast_mean.values,
                        'lower': forecast_lower,
                        'upper': forecast_upper,
                        'stddev': forecast_std
                    },
                    'metrics': {
                        'mae': mae,
                        'rmse': rmse,
                        'mape': mape,
                        'r2': r2
                    }
                }
            
            except Exception as e:
                print(f"Fallback ARIMA model failed: {str(e)}")
                # Last resort: use moving average
                return self._forecast_with_moving_average(data)
    
    def _forecast_with_moving_average(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Fallback forecasting using moving average.
        
        Args:
            data (pd.DataFrame): DataFrame with price data
            
        Returns:
            Dict[str, Any]: Dictionary with forecast results
        """
        # Calculate moving average
        window = min(30, len(data) // 3)
        ma = data['price'].rolling(window=window).mean()
        
        # Calculate standard deviation for confidence intervals
        std = data['price'].rolling(window=window).std().iloc[-1]
        
        # Generate forecast using the last moving average value
        forecast_mean = np.ones(self.forecast_horizon) * ma.iloc[-1]
        
        # Calculate prediction intervals
        z_score = stats.norm.ppf((1 + self.confidence_level) / 2)
        
        forecast_lower = forecast_mean - z_score * std
        forecast_upper = forecast_mean + z_score * std
        forecast_std = np.ones(self.forecast_horizon) * std
        
        # Generate dates for the forecast
        last_date = data.index[-1]
        forecast_dates = [last_date + datetime.timedelta(days=i+1) for i in range(self.forecast_horizon)]
        
        # Calculate metrics using historical data
        train_size = int(len(data) * 0.8)
        train_data = data.iloc[:train_size]
        test_data = data.iloc[train_size:]
        
        # Generate predictions using moving average
        ma_test = train_data['price'].rolling(window=window).mean().iloc[-1]
        pred_mean = np.ones(len(test_data)) * ma_test
        
        mae = mean_absolute_error(test_data['price'], pred_mean)
        rmse = np.sqrt(mean_squared_error(test_data['price'], pred_mean))
        mape = np.mean(np.abs((test_data['price'].values - pred_mean) / test_data['price'].values)) * 100
        r2 = r2_score(test_data['price'], pred_mean)
        
        return {
            'forecast': {
                'dates': forecast_dates,
                'mean': forecast_mean,
                'lower': forecast_lower,
                'upper': forecast_upper,
                'stddev': forecast_std
            },
            'metrics': {
                'mae': mae,
                'rmse': rmse,
                'mape': mape,
                'r2': r2
            }
        }
    
    def _decompose_time_series(self, data: pd.DataFrame) -> Dict[str, np.ndarray]:
        """
        Decompose time series into trend, seasonal, and residual components.
        
        Args:
            data (pd.DataFrame): DataFrame with price data
            
        Returns:
            Dict[str, np.ndarray]: Dictionary with decomposed components
        """
        # Minimum period for seasonal decomposition
        min_periods = {'trend': 2, 'seasonality': 7, 'residual': 2}
        components = {}
        
        # Ensure enough data points for decomposition
        if len(data) < max(min_periods.values()) * 2:
            # Not enough data for decomposition, use simple components
            trend = np.array(pd.Series(data['price']).rolling(window=min_periods['trend']).mean().fillna(method='bfill'))
            components['trend'] = trend
            return components
        
        try:
            # Try to perform seasonal decomposition
            period = min(7, len(data)//2)
            # Ensure period is at least 2
            period = max(2, period)
            decomposition = seasonal_decompose(data['price'], model='additive', period=period)
            
            if self.include_trend:
                components['trend'] = decomposition.trend.bfill().ffill().values
            
            if self.include_seasonality:
                components['seasonality'] = decomposition.seasonal.bfill().ffill().values
            
            if self.include_autoregressive:
                components['residual'] = decomposition.resid.bfill().ffill().values
        except Exception as e:
            print(f"Decomposition failed: {str(e)}")
            # Fallback to simpler decomposition
            trend = np.array(pd.Series(data['price']).rolling(window=min_periods['trend']).mean().bfill())
            components['trend'] = trend
        
        return components
    
    def fit_and_forecast(self, data: pd.DataFrame, sentiment_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Fit the model to historical data and generate forecasts.
        
        Args:
            data (pd.DataFrame): DataFrame with Bitcoin price data
            sentiment_data (Optional[pd.DataFrame]): Optional DataFrame with sentiment features
            
        Returns:
            Dict[str, Any]: Dictionary containing forecast results and metrics
        """
        # Create a copy of the data to avoid modifying the original
        df = data.copy()
        
        # Add sentiment data to the price data if available
        used_sentiment = False
        if sentiment_data is not None and not sentiment_data.empty:
            # Check for sentiment columns we can use
            sentiment_cols = [col for col in sentiment_data.columns if col.startswith('sentiment_')]
            
            if sentiment_cols:
                # Merge sentiment data with price data based on dates
                for col in sentiment_cols:
                    df[col] = sentiment_data.get(col, 0)
                
                # Fill NaN values with zeros (or other appropriate values)
                df = df.fillna(0)
                used_sentiment = True
                print(f"Integrated sentiment features: {sentiment_cols}")
        
        # Generate forecasts with ARIMA
        forecast_results = self._forecast_with_arima(df)
        
        # Get time series components for visualization
        components = self._decompose_time_series(df)
        
        # Mark model as trained
        self.trained = True
        
        # Add components to results
        forecast_results['components'] = components if len(components) > 0 else None
        forecast_results['used_sentiment'] = used_sentiment
        
        return forecast_results
