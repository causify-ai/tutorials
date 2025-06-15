#!/usr/bin/env python3
"""
Model utility functions for the Bitcoin forecasting system.
Provides helper functions for model operations and handling specific data types.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from typing import Union, Any, Tuple, List, Dict, Optional
import logging

from utilities.data_utils import safe_round, ensure_tz_aware

logger = logging.getLogger(__name__)

def extract_scalar_from_prediction(prediction: Any) -> float:
    """
    Extract a scalar value from a prediction which might be a numpy array.
    
    Args:
        prediction: A prediction value from a model
        
    Returns:
        A scalar float value
    """
    if isinstance(prediction, np.ndarray):
        if prediction.size == 1:
            return float(prediction.item())
        elif prediction.size > 1:
            return float(prediction[0])  # Take first element
    
    try:
        return float(prediction)
    except (TypeError, ValueError):
        logger.warning(f"Could not convert prediction to float: {prediction}")
        return 0.0

def validate_confidence_interval(
    mean_pred: Any,
    lower_bound: Any,
    upper_bound: Any,
    min_interval: float = 10.0
) -> Tuple[float, float, float]:
    """
    Validate a confidence interval, ensuring it is in the correct order and has a minimum width.
    
    Args:
        mean_pred: Mean prediction value
        lower_bound: Lower bound of confidence interval
        upper_bound: Upper bound of confidence interval
        min_interval: Minimum interval width (default: 10.0)
        
    Returns:
        Tuple of (mean, lower, upper) as floats
    """
    # Convert all values to float
    mean = extract_scalar_from_prediction(mean_pred)
    lower = extract_scalar_from_prediction(lower_bound)
    upper = extract_scalar_from_prediction(upper_bound)
    
    # Ensure lower bound is actually lower than upper bound
    if lower > upper:
        lower, upper = upper, lower
    
    # Ensure the interval has a minimum width
    current_width = upper - lower
    if current_width < min_interval:
        # Expand interval symmetrically around the mean
        half_min_width = min_interval / 2
        lower = mean - half_min_width
        upper = mean + half_min_width
    
    return mean, lower, upper

def safe_model_prediction(
    model: Any,
    method_name: str = 'forecast',
    fallback_value: float = 100000.0,
    *args,
    **kwargs
) -> Tuple[float, float, float]:
    """
    Safely call a model's prediction method with error handling.
    
    Args:
        model: The model object
        method_name: Name of the prediction method to call (default: 'forecast')
        fallback_value: Value to use if prediction fails
        *args, **kwargs: Arguments to pass to the prediction method
        
    Returns:
        Tuple of (prediction, lower_bound, upper_bound)
    """
    try:
        # Check if the model exists and has the method
        if model is None or not hasattr(model, method_name):
            logger.warning(f"Model is None or does not have method {method_name}, using fallback value")
            # Return fallback with a 1% confidence interval
            return fallback_value, fallback_value * 0.99, fallback_value * 1.01
        
        # Call the method with the provided arguments
        method = getattr(model, method_name)
        result = method(*args, **kwargs)
        
        # Handle different return types
        if isinstance(result, tuple) and len(result) >= 3:
            # Method returns prediction and confidence bounds
            pred, lower, upper = result[0], result[1], result[2]
            return validate_confidence_interval(pred, lower, upper)
        elif isinstance(result, tuple) and len(result) == 2:
            # Method returns prediction and some uncertainty measure
            pred, uncertainty = result[0], result[1]
            lower = extract_scalar_from_prediction(pred) - extract_scalar_from_prediction(uncertainty)
            upper = extract_scalar_from_prediction(pred) + extract_scalar_from_prediction(uncertainty)
            return validate_confidence_interval(pred, lower, upper)
        else:
            # Method returns just a prediction
            pred = extract_scalar_from_prediction(result)
            # Assume a 1% confidence interval
            return pred, pred * 0.99, pred * 1.01
            
    except Exception as e:
        logger.error(f"Error in safe_model_prediction: {e}")
        # Return fallback with a 1% confidence interval
        return fallback_value, fallback_value * 0.99, fallback_value * 1.01

def calculate_error_metrics(
    actual: float,
    predicted: float
) -> Dict[str, float]:
    """
    Calculate error metrics between actual and predicted values.
    
    Args:
        actual: Actual value
        predicted: Predicted value
        
    Returns:
        Dictionary of error metrics
    """
    try:
        # Extract scalar values
        actual_val = extract_scalar_from_prediction(actual)
        pred_val = extract_scalar_from_prediction(predicted)
        
        # Calculate error
        error = actual_val - pred_val
        abs_error = abs(error)
        
        # Calculate percentage error
        if actual_val != 0:
            pct_error = (error / actual_val) * 100
        else:
            pct_error = float('inf')
        
        # Calculate squared error
        squared_error = error ** 2
        
        return {
            'error': error,
            'absolute_error': abs_error,
            'percentage_error': pct_error,
            'squared_error': squared_error
        }
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        return {
            'error': 0.0,
            'absolute_error': 0.0,
            'percentage_error': 0.0,
            'squared_error': 0.0
        } 