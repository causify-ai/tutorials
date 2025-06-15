#!/usr/bin/env python3
"""
Test script for the utility functions.
Run this to verify the utility functions are working properly.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timezone, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("utils_test")

# Import utilities
try:
    from data_utils import (
        safe_round, ensure_tz_aware, normalize_timestamps,
        compare_timestamps, filter_by_timestamp, format_price
    )
    from model_utils import (
        extract_scalar_from_prediction, validate_confidence_interval,
        safe_model_prediction, calculate_error_metrics
    )
except ImportError:
    # Try with full path
    from utilities.data_utils import (
        safe_round, ensure_tz_aware, normalize_timestamps,
        compare_timestamps, filter_by_timestamp, format_price
    )
    from utilities.model_utils import (
        extract_scalar_from_prediction, validate_confidence_interval,
        safe_model_prediction, calculate_error_metrics
    )

def test_data_utils():
    """Test data utility functions."""
    logger.info("Testing data utility functions...")
    
    # Test safe_round with different types
    assert safe_round(5.678) == 5.68
    assert safe_round(np.array([5.678])) == 5.68
    assert safe_round(np.array([5.678, 6.789]), 1) == 5.7
    
    # Test ensure_tz_aware
    naive_dt = datetime(2025, 5, 15, 12, 30, 0)
    aware_dt = ensure_tz_aware(naive_dt)
    assert aware_dt.tzinfo is not None
    
    # Test normalize_timestamps
    dates = [datetime(2025, 5, 15), datetime(2025, 5, 16)]
    df = pd.DataFrame({'timestamp': dates})
    normalized_df = normalize_timestamps(df)
    assert normalized_df['timestamp'].dt.tz is not None
    
    # Test compare_timestamps
    dt1 = datetime(2025, 5, 15, 12, 0, 0, tzinfo=timezone.utc)
    dt2 = datetime(2025, 5, 15, 11, 0, 0)  # Naive
    assert compare_timestamps(dt1, dt2) is True
    
    # Test filter_by_timestamp
    df = pd.DataFrame({
        'timestamp': pd.date_range(start='2025-05-15', periods=5, freq='D')
    })
    cutoff = datetime(2025, 5, 17)
    filtered_df = filter_by_timestamp(df, cutoff)
    assert len(filtered_df) == 3  # 17th, 18th, 19th
    
    # Test format_price
    assert format_price(123.456) == "123.46"
    assert format_price(np.array([123.456])) == "123.46"
    
    logger.info("Data utility tests passed!")

def test_model_utils():
    """Test model utility functions."""
    logger.info("Testing model utility functions...")
    
    # Test extract_scalar_from_prediction
    assert extract_scalar_from_prediction(5.67) == 5.67
    assert extract_scalar_from_prediction(np.array([5.67])) == 5.67
    assert extract_scalar_from_prediction(np.array([5.67, 6.78])) == 5.67
    
    # Test validate_confidence_interval
    mean, lower, upper = validate_confidence_interval(100.0, 95.0, 105.0)
    assert mean == 100.0
    assert lower == 95.0
    assert upper == 105.0
    
    # Test with incorrect order
    mean, lower, upper = validate_confidence_interval(100.0, 105.0, 95.0)
    assert mean == 100.0
    assert lower == 95.0
    assert upper == 105.0
    
    # Test with too narrow interval
    mean, lower, upper = validate_confidence_interval(100.0, 99.0, 101.0, min_interval=10.0)
    assert mean == 100.0
    assert upper - lower >= 10.0
    
    # Test calculate_error_metrics
    metrics = calculate_error_metrics(100.0, 95.0)
    assert metrics['error'] == 5.0
    assert metrics['absolute_error'] == 5.0
    assert metrics['percentage_error'] == 5.0
    
    # Test with numpy arrays
    metrics = calculate_error_metrics(np.array([100.0]), np.array([95.0]))
    assert metrics['error'] == 5.0
    
    logger.info("Model utility tests passed!")

class MockModel:
    """Mock model for testing safe_model_prediction."""
    def forecast(self):
        """Return a mock forecast."""
        return 100.0, 95.0, 105.0
    
    def forecast_array(self):
        """Return a mock forecast with numpy arrays."""
        return np.array([100.0]), np.array([95.0]), np.array([105.0])
    
    def forecast_single(self):
        """Return just a prediction without bounds."""
        return 100.0
    
    def non_existent(self):
        """This method won't be called."""
        pass

def test_safe_model_prediction():
    """Test safe_model_prediction function."""
    logger.info("Testing safe_model_prediction...")
    
    model = MockModel()
    
    # Test with existing method returning tuple
    pred, lower, upper = safe_model_prediction(model, 'forecast')
    assert pred == 100.0
    assert lower == 95.0
    assert upper == 105.0
    
    # Test with numpy arrays
    pred, lower, upper = safe_model_prediction(model, 'forecast_array')
    assert pred == 100.0
    assert lower == 95.0
    assert upper == 105.0
    
    # Test with method returning single value
    pred, lower, upper = safe_model_prediction(model, 'forecast_single')
    assert pred == 100.0
    assert lower < pred
    assert upper > pred
    
    # Test with non-existent method
    pred, lower, upper = safe_model_prediction(model, 'nonexistent_method')
    assert pred == 100000.0  # Default fallback
    
    # Test with None model
    pred, lower, upper = safe_model_prediction(None, 'forecast')
    assert pred == 100000.0  # Default fallback
    
    logger.info("safe_model_prediction tests passed!")

if __name__ == "__main__":
    try:
        logger.info("Starting utility tests...")
        
        test_data_utils()
        test_model_utils()
        test_safe_model_prediction()
        
        logger.info("All utility tests passed!")
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        logger.error(traceback.format_exc()) 