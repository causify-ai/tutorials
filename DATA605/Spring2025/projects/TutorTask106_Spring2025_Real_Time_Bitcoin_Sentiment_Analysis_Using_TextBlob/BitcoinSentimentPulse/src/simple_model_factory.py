"""
Simple Model Factory for Bitcoin Price Forecasting

This module provides a factory class that creates ARIMA-based
forecasting models for all model types as a safe fallback.
"""

import logging
from typing import Dict, List, Any, Optional

# Import only the ARIMA model
from src.model import BitcoinForecastModel

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
        return [cls.ARIMA, cls.LSTM, cls.TRANSFORMER, cls.ENSEMBLE]

class SimpleModelFactory:
    """
    Factory class for creating forecasting models.
    Only supports ARIMA models but accepts parameters for other types
    as fallback for environments where TensorFlow isn't available.
    """
    
    def __init__(self):
        """Initialize the model factory"""
        self.cached_models = {}
    
    def create_model(self, model_type: str, **kwargs) -> Any:
        """
        Create a model based on type (all types fall back to ARIMA)
        
        Args:
            model_type (str): Type of model to create (all use ARIMA)
            **kwargs: Model-specific parameters
            
        Returns:
            BitcoinForecastModel instance
        """
        model_type = model_type.lower()
        
        # Check if model type is valid
        if model_type not in ModelType.all():
            raise ValueError(f"Unknown model type: {model_type}. Available types: {ModelType.all()}")
        
        # Filter model-specific parameters for ARIMA
        arima_params = {}
        
        # Extract common parameters that work with ARIMA model
        for param in ['forecast_horizon', 'confidence_level', 'use_mcmc', 
                      'include_trend', 'include_seasonality', 'include_autoregressive']:
            if param in kwargs:
                arima_params[param] = kwargs[param]
        
        # Log message for non-ARIMA models
        if model_type != ModelType.ARIMA:
            logger.warning(f"{model_type} model requested but using ARIMA as fallback.")
        
        # Create and return ARIMA model with filtered parameters
        return BitcoinForecastModel(**arima_params)
    
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


# For backwards compatibility
ModelFactory = SimpleModelFactory