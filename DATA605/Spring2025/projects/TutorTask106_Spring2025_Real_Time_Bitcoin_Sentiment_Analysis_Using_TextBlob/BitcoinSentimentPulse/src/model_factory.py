"""
Model Factory for Bitcoin Price Forecasting

This module provides a factory class that creates different types of
forecasting models based on the requested type.
"""

import logging
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np

# Import all model types
from src.model import BitcoinForecastModel
from src.lstm_model import BitcoinLSTMModel
from src.transformer_model import BitcoinTransformerModel
from src.ensemble_model import BitcoinEnsembleModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelType:
    """Constants for model types"""
    ARIMA = "arima"
    LSTM = "lstm"
    TRANSFORMER = "transformer"
    ENSEMBLE = "ensemble"
    
    @classmethod
    def all(cls) -> List[str]:
        """Get list of all available model types"""
        return [cls.ARIMA, cls.LSTM]# cls.TRANSFORMER, cls.ENSEMBLE]

class ModelFactory:
    """
    Factory class for creating forecasting models.
    """
    
    def __init__(self):
        """Initialize the model factory"""
        self.cached_models = {}
    
    def create_model(self, model_type: str, **kwargs) -> Any:
        """
        Create a model based on type.
        
        Args:
            model_type (str): Type of model to create
            **kwargs: Model-specific parameters
            
        Returns:
            Model instance
        """
        model_type = model_type.lower()
        
        # Check if model type is valid
        if model_type not in ModelType.all():
            raise ValueError(f"Unknown model type: {model_type}. Available types: {ModelType.all()}")
        
        # Initialize model parameters dictionary
        model_params = {}
        
        if model_type == ModelType.ARIMA:
            # ARIMA-specific parameters
            for param in ['forecast_horizon', 'use_mcmc', 'include_trend', 
                         'include_seasonality', 'include_autoregressive', 'confidence_level']:
                if param in kwargs:
                    model_params[param] = kwargs[param]
            return BitcoinForecastModel(**model_params)
            
        elif model_type == ModelType.LSTM:
            # LSTM-specific parameters
            for param in ['forecast_horizon', 'lookback_window', 'hidden_units',
                         'dropout_rate', 'learning_rate', 'batch_size', 'epochs',
                         'include_sentiment']:
                if param in kwargs:
                    model_params[param] = kwargs[param]
            return BitcoinLSTMModel(**model_params)
            
        elif model_type == ModelType.TRANSFORMER:
            # Transformer-specific parameters
            for param in ['forecast_horizon', 'lookback_window', 'embed_dim',
                         'num_heads', 'ff_dim', 'num_transformer_blocks', 'mlp_units',
                         'dropout_rate', 'mlp_dropout_rate', 'learning_rate',
                         'batch_size', 'epochs', 'include_sentiment']:
                if param in kwargs:
                    model_params[param] = kwargs[param]
            return BitcoinTransformerModel(**model_params)
            
        elif model_type == ModelType.ENSEMBLE:
            # Create individual models for ensemble
            models = []
            weights = []
            
            # Create ARIMA model
            arima_params = {k: v for k, v in kwargs.items() 
                          if k in ['forecast_horizon', 'use_mcmc', 'include_trend', 
                                 'include_seasonality', 'include_autoregressive', 'confidence_level']}
            models.append(BitcoinForecastModel(**arima_params))
            weights.append(0.4)  # ARIMA weight
            
            # Create LSTM model if TensorFlow is available
            try:
                lstm_params = {k: v for k, v in kwargs.items() 
                             if k in ['forecast_horizon', 'lookback_window', 'hidden_units',
                                    'dropout_rate', 'learning_rate', 'batch_size', 'epochs',
                                    'include_sentiment']}
                models.append(BitcoinLSTMModel(**lstm_params))
                weights.append(0.3)  # LSTM weight
            except ImportError:
                print("TensorFlow not available, skipping LSTM model")
            
            # Create Transformer model if TensorFlow is available
            try:
                transformer_params = {k: v for k, v in kwargs.items() 
                                   if k in ['forecast_horizon', 'lookback_window', 'embed_dim',
                                          'num_heads', 'ff_dim', 'num_transformer_blocks', 'mlp_units',
                                          'dropout_rate', 'mlp_dropout_rate', 'learning_rate',
                                          'batch_size', 'epochs', 'include_sentiment']}
                models.append(BitcoinTransformerModel(**transformer_params))
                weights.append(0.3)  # Transformer weight
            except ImportError:
                print("TensorFlow not available, skipping Transformer model")
            
            # Normalize weights
            weights = [w/sum(weights) for w in weights]
            
            return BitcoinEnsembleModel(models, weights)
    
    def get_model(self, model_type: str, **kwargs) -> Any:
        """
        Get a model instance, either from cache or by creating a new one.
        
        Args:
            model_type (str): Type of model to get
            **kwargs: Model-specific parameters
            
        Returns:
            Model instance
        """
        # Create a cache key based on model type and parameters
        cache_key = f"{model_type}_{hash(frozenset(kwargs.items()))}"
        
        # Check if model exists in cache
        if cache_key in self.cached_models:
            return self.cached_models[cache_key]
        
        # Create new model
        model = self.create_model(model_type, **kwargs)
        
        # Cache model for future use
        self.cached_models[cache_key] = model
        
        return model

class EnsembleModel:
    """
    Ensemble model that combines multiple forecasting models.
    
    Attributes:
        models (List): List of model instances
        weights (List[float]): Weights for each model
        include_sentiment (bool): Whether to include sentiment in forecasts
    """
    
    def __init__(
        self,
        model_types: List[str] = None,
        weights: List[float] = None,
        forecast_horizon: int = 7,
        include_sentiment: bool = True,
        **kwargs
    ):
        """
        Initialize the ensemble model.
        
        Args:
            model_types (List[str]): List of model types to include
            weights (List[float]): Weights for each model (will be normalized)
            forecast_horizon (int): Number of days to forecast
            include_sentiment (bool): Whether to include sentiment
            **kwargs: Additional parameters passed to each model
        """
        self.forecast_horizon = forecast_horizon
        self.include_sentiment = include_sentiment
        
        # In this environment, we only support ARIMA models
        # regardless of what is requested
        logger.warning("Advanced models not available. Using only ARIMA for ensemble.")
        self.model_types = [ModelType.ARIMA]
        
        # Set default weights if not provided (equal weighting)
        if weights is None:
            self.weights = [1.0] * len(self.model_types)
        else:
            if len(weights) != len(self.model_types):
                raise ValueError("Number of weights must match number of models")
            self.weights = weights
        
        # Normalize weights
        total_weight = sum(self.weights)
        self.weights = [w / total_weight for w in self.weights]
        
        # Create model instances
        self.factory = ModelFactory()
        self.models = []
        
        for model_type in self.model_types:
            if model_type != ModelType.ENSEMBLE:  # Prevent recursive ensembles
                # Set common parameters
                model_kwargs = kwargs.copy()
                model_kwargs['forecast_horizon'] = forecast_horizon
                model_kwargs['include_sentiment'] = include_sentiment
                
                # Create model
                model = self.factory.create_model(model_type, **model_kwargs)
                self.models.append(model)
    
    def fit_and_forecast(self, data: pd.DataFrame, sentiment_data: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        Fit models and generate ensemble forecast.
        
        Args:
            data (pd.DataFrame): DataFrame with Bitcoin price data
            sentiment_data (Optional[pd.DataFrame]): Optional DataFrame with sentiment features
            
        Returns:
            Dict[str, Any]: Dictionary with forecast results and metrics
        """
        try:
            if not self.models:
                raise ValueError("No models in ensemble")
            
            # Run forecasts for all models
            forecasts = []
            metrics = []
            
            for i, model in enumerate(self.models):
                result = model.fit_and_forecast(data, sentiment_data)
                
                if 'forecast' in result and not result['forecast'].empty:
                    forecasts.append(result['forecast'])
                    metrics.append(result['metrics'])
                else:
                    logger.warning(f"Model {self.model_types[i]} failed to produce forecast")
            
            if not forecasts:
                logger.error("All models failed to produce forecasts")
                raise ValueError("No valid forecasts produced by any model")
            
            # Get dates from first forecast
            dates = forecasts[0].index
            
            # Create weighted ensemble forecast
            ensemble_forecast = pd.DataFrame(index=dates)
            ensemble_forecast['Forecast'] = 0.0
            ensemble_forecast['Lower_CI'] = 0.0
            ensemble_forecast['Upper_CI'] = 0.0
            
            # Weight and combine forecasts
            valid_weights_sum = 0
            valid_forecasts = []
            valid_weights = []
            
            for i, forecast_df in enumerate(forecasts):
                # Skip if forecast shape doesn't match
                if len(forecast_df) != len(dates):
                    logger.warning(f"Skipping forecast from {self.model_types[i]} due to shape mismatch")
                    continue
                
                valid_forecasts.append(forecast_df)
                valid_weights.append(self.weights[i])
                valid_weights_sum += self.weights[i]
            
            # Re-normalize valid weights
            if valid_weights:
                valid_weights = [w / valid_weights_sum for w in valid_weights]
            
            # Combine valid forecasts
            for i, forecast_df in enumerate(valid_forecasts):
                weight = valid_weights[i]
                ensemble_forecast['Forecast'] += weight * forecast_df['Forecast']
                ensemble_forecast['Lower_CI'] += weight * forecast_df['Lower_CI']
                ensemble_forecast['Upper_CI'] += weight * forecast_df['Upper_CI']
            
            # Calculate ensemble metrics
            ensemble_metrics = {
                'model_type': 'Ensemble',
                'forecast_horizon': self.forecast_horizon,
                'used_sentiment': self.include_sentiment and sentiment_data is not None,
                'models_used': [self.model_types[i] for i in range(len(forecasts)) if i < len(self.model_types)],
                'weights_used': valid_weights
            }
            
            # Add averaged metrics from individual models
            avg_metrics = {}
            for metric in ['rmse', 'val_loss', 'train_loss']:
                values = [m.get(metric, 0) for m in metrics if metric in m]
                if values:
                    avg_metrics[f'avg_{metric}'] = sum(values) / len(values)
            
            ensemble_metrics.update(avg_metrics)
            
            return {
                'forecast': ensemble_forecast,
                'metrics': ensemble_metrics,
                'individual_forecasts': valid_forecasts,
                'individual_metrics': metrics,
                'used_sentiment': self.include_sentiment and sentiment_data is not None
            }
            
        except Exception as e:
            logger.error(f"Error in ensemble model: {str(e)}")
            # Fallback to empty forecast
            return {
                'forecast': pd.DataFrame(),
                'metrics': {'error': str(e)},
                'used_sentiment': False
            }

# Test code (remove in production)
if __name__ == "__main__":
    import pandas as pd
    import numpy as np
    
    # Create synthetic data
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    close_prices = np.random.normal(20000, 1000, 100) + np.linspace(0, 2000, 100)
    
    # Create DataFrame
    df = pd.DataFrame({
        'Close': close_prices
    }, index=dates)
    
    # Test model factory
    factory = ModelFactory()
    
    # Test creating models
    arima_model = factory.create_model(ModelType.ARIMA, forecast_horizon=7)
    lstm_model = factory.create_model(ModelType.LSTM, forecast_horizon=7, lookback_window=14)
    
    # Test ensemble
    ensemble = factory.create_model(
        ModelType.ENSEMBLE,
        model_types=[ModelType.ARIMA, ModelType.LSTM],
        weights=[0.7, 0.3],
        forecast_horizon=7
    )
    
    # Test forecast
    result = ensemble.fit_and_forecast(df)
    print(result['forecast'])