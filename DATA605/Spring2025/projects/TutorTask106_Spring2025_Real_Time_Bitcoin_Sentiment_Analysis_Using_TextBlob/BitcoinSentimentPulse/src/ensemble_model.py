"""
Ensemble Model for Bitcoin Price Forecasting

This module implements an ensemble model that combines predictions
from multiple models (ARIMA, LSTM, Transformer) with weighted averaging.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BitcoinEnsembleModel:
    """
    Ensemble model that combines multiple forecasting models.
    
    Attributes:
        models (List): List of model instances
        weights (List[float]): Weights for each model's predictions
    """
    
    def __init__(self, models: List[Any], weights: Optional[List[float]] = None):
        """
        Initialize the ensemble model.
        
        Args:
            models (List): List of model instances
            weights (Optional[List[float]]): Weights for each model's predictions.
                                           If None, equal weights are used.
        """
        self.models = models
        
        # Normalize weights if provided
        if weights is not None:
            self.weights = np.array(weights) / sum(weights)
        else:
            self.weights = np.ones(len(models)) / len(models)
    
    def fit_and_forecast(self, data: pd.DataFrame, sentiment_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Fit all models and generate ensemble forecast.
        
        Args:
            data (pd.DataFrame): DataFrame with Bitcoin price data
            sentiment_data (Optional[pd.DataFrame]): Optional DataFrame with sentiment features
            
        Returns:
            Dict[str, Any]: Dictionary with forecast results and evaluation metrics
        """
        try:
            # Get forecasts from each model
            forecasts = []
            metrics = []
            
            for model in self.models:
                # Get forecast from individual model
                result = model.fit_and_forecast(data, sentiment_data)
                forecasts.append(result['forecast'])
                metrics.append(result['metrics'])
            
            # Combine forecasts using weighted average
            if isinstance(forecasts[0], pd.DataFrame):
                # For DataFrame forecasts (new format)
                combined_forecast = pd.DataFrame(index=forecasts[0].index)
                for col in forecasts[0].columns:
                    combined_forecast[col] = sum(f[col] * w for f, w in zip(forecasts, self.weights))
            else:
                # For dictionary forecasts (old format)
                combined_forecast = {
                    'dates': forecasts[0]['dates'],
                    'mean': sum(f['mean'] * w for f, w in zip(forecasts, self.weights)),
                    'lower': sum(f['lower'] * w for f, w in zip(forecasts, self.weights)),
                    'upper': sum(f['upper'] * w for f, w in zip(forecasts, self.weights))
                }
            
            # Combine metrics using weighted average
            combined_metrics = {
                'mae': sum(m['mae'] * w for m, w in zip(metrics, self.weights)),
                'rmse': sum(m['rmse'] * w for m, w in zip(metrics, self.weights)),
                'mape': sum(m['mape'] * w for m, w in zip(metrics, self.weights)),
                'r2': sum(m['r2'] * w for m, w in zip(metrics, self.weights))
            }
            
            return {
                'forecast': combined_forecast,
                'metrics': combined_metrics,
                'individual_forecasts': forecasts,
                'individual_metrics': metrics,
                'used_sentiment': any(m.get('used_sentiment', False) for m in metrics)
            }
            
        except Exception as e:
            logger.error(f"Error in ensemble forecasting: {str(e)}")
            raise 