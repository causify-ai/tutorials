import tensorflow as tf
import tensorflow_transform as tft
import numpy as np
from typing import Dict, Text

# Feature keys
PRICE_KEY = 'price'
TRANSFORMED_PRICE_KEY = 'normalized_price'

def _fill_in_missing(x):
    """Replace missing values with 0, handling both numeric types."""
    if x is None:
        return tf.zeros([], dtype=tf.float32)
    x = tf.cast(x, tf.float32)
    return tf.where(tf.math.is_nan(x), tf.zeros_like(x), x)

def preprocessing_fn(inputs: Dict[Text, tf.Tensor]) -> Dict[Text, tf.Tensor]:
    """Transform raw input features into model-ready features.
    
    This function preprocesses the raw Bitcoin price data into features
    that are suitable for model training. It:
    1. Normalizes the price using z-score normalization
    2. Creates cyclical time features (hour, day of week)
    3. Creates volatility features from price changes
    4. Handles any missing values appropriately
    
    Args:
        inputs: A dictionary of input tensors keyed by feature name
        
    Returns:
        A dictionary of transformed features
    """
    outputs = {}

    # Normalize price (main target/feature)
    price = _fill_in_missing(inputs.get(PRICE_KEY))
    outputs[TRANSFORMED_PRICE_KEY] = tft.scale_to_z_score(price)

    # Process moving average if available
    if 'rolling_mean_24h' in inputs:
        ma = _fill_in_missing(inputs['rolling_mean_24h'])
        outputs['normalized_ma_24h'] = tft.scale_to_z_score(ma)

    # Process price change and create volatility features if available
    if 'price_change' in inputs:
        price_change = _fill_in_missing(inputs['price_change'])
        outputs['volatility_bucket'] = tf.cast(
            tft.bucketize(tf.abs(price_change), num_buckets=10),
            tf.float32
        )
        outputs['volatility_normalized'] = tft.scale_to_z_score(tf.abs(price_change))
        
        # Direction of change (up/down) as binary feature
        outputs['price_direction'] = tf.cast(
            tf.greater_equal(price_change, 0.0),
            tf.float32
        )

    # Create cyclical time features from hour
    if 'hour' in inputs:
        hour = tf.cast(inputs['hour'], tf.float32)
        # Convert hours to cyclical representation using sine and cosine
        outputs['hour_sin'] = tf.sin(2 * np.pi * hour / 24.0)
        outputs['hour_cos'] = tf.cos(2 * np.pi * hour / 24.0)

    # Create cyclical time features from day of week
    if 'day_of_week' in inputs:
        day = tf.cast(inputs['day_of_week'], tf.float32)
        # Convert day of week to cyclical representation using sine and cosine
        outputs['day_sin'] = tf.sin(2 * np.pi * day / 7.0)
        outputs['day_cos'] = tf.cos(2 * np.pi * day / 7.0)

    return outputs