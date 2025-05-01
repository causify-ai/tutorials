import tensorflow as tf
import tensorflow_transform as tft
from typing import List, Text, Dict, Any


PRICE_KEY = 'price'  
TIMESTAMP_KEY = 'timestamp'  

TRANSFORMED_PRICE_KEY = 'normalized_price'


def _fill_in_missing(x):
    """Replace missing values with 0."""
    return tf.where(tf.math.is_nan(x), tf.zeros_like(x), x)


def preprocessing_fn(inputs: Dict[Text, tf.Tensor]) -> Dict[Text, tf.Tensor]:
    """Preprocess the features using TensorFlow Transform.
    
    Args:
        inputs: A dictionary of input tensors
        
    Returns:
        A dictionary of transformed tensors
    """
    outputs = {}
    
    price = _fill_in_missing(inputs.get(PRICE_KEY, tf.constant([], dtype=tf.float32)))
    
    normalized_price = tft.scale_to_0_1(price)
    
    outputs[TRANSFORMED_PRICE_KEY] = normalized_price
    
    
    tf.print(f"Input shape for {PRICE_KEY}:", tf.shape(price))
    tf.print(f"Output shape for {TRANSFORMED_PRICE_KEY}:", tf.shape(normalized_price))
    
    return outputs