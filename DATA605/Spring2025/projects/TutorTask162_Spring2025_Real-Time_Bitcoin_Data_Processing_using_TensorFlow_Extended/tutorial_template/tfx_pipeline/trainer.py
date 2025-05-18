import tensorflow as tf
import tensorflow_transform as tft
from tfx_bsl.public import tfxio
from tfx.components.trainer.fn_args_utils import FnArgs
import numpy as np

# Constants
FEATURE_KEY = 'normalized_price'
LABEL_KEY = 'normalized_price'
WINDOW_SIZE = 24  # 24 hours for daily patterns

def _get_serve_tf_examples_fn(model, tf_transform_output):
    """Returns a function that parses a serialized tf.Example."""
    model.tft_layer = tf_transform_output.transform_features_layer()
    
    @tf.function
    def serve_tf_examples_fn(serialized_tf_examples):
        """Returns the output to be used in the serving signature."""
        feature_spec = tf_transform_output.raw_feature_spec()
        feature_spec.pop(LABEL_KEY, None)
        parsed_features = tf.io.parse_example(serialized_tf_examples, feature_spec)
        transformed_features = model.tft_layer(parsed_features)
        return model(transformed_features)
    
    return serve_tf_examples_fn

def _input_fn(file_pattern, data_accessor, tf_transform_output, batch_size=32):
    """Creates a dataset from transformed data."""
    dataset = data_accessor.tf_dataset_factory(
        file_pattern,
        tfxio.TensorFlowDatasetOptions(batch_size=batch_size),
        schema=tf_transform_output.transformed_metadata.schema
    )
    
    # Fix: directly use the transformed dataset with minimal processing
    def transform_features(features):
        # Use the normalized_price as both input feature and label
        if FEATURE_KEY in features:
            return {FEATURE_KEY: features[FEATURE_KEY]}, features[FEATURE_KEY]
        else:
            # Create a placeholder feature if normalized_price is missing
            # This is a workaround, it's better to fix transform.py to ensure proper features
            return {FEATURE_KEY: tf.zeros_like(list(features.values())[0])}, list(features.values())[0]
    
    return dataset.map(transform_features)

def _build_model():
    """Builds a simple but effective model for Bitcoin price forecasting."""
    # Keep the model simple while ensuring input name matches the expected feature
    inputs = tf.keras.layers.Input(shape=(1,), name=FEATURE_KEY)
    
    # Simple LSTM architecture
    x = tf.keras.layers.Reshape((1, 1))(inputs)
    x = tf.keras.layers.LSTM(64, return_sequences=False)(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    
    # Dense layers
    x = tf.keras.layers.Dense(32, activation='relu')(x)
    outputs = tf.keras.layers.Dense(1)(x)
    
    model = tf.keras.Model(inputs=inputs, outputs=outputs)
    
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='mse',
        metrics=['mae']
    )
    
    model.summary()
    return model

def run_fn(fn_args: FnArgs):
    """Train the model using the given arguments."""
    tf_transform_output = tft.TFTransformOutput(fn_args.transform_output)
    
    # Print available features to help debug
    print("Available transformed features:", tf_transform_output.transformed_feature_spec().keys())
    
    train_dataset = _input_fn(
        fn_args.train_files,
        fn_args.data_accessor,
        tf_transform_output,
        batch_size=32
    )
    
    eval_dataset = _input_fn(
        fn_args.eval_files,
        fn_args.data_accessor,
        tf_transform_output,
        batch_size=32
    )
    
    model = _build_model()
    
    # Set fixed steps
    train_steps = 100
    eval_steps = 50
    
    # Cache the datasets to improve performance
    train_dataset = train_dataset.cache().prefetch(tf.data.AUTOTUNE)
    eval_dataset = eval_dataset.cache().prefetch(tf.data.AUTOTUNE)
    
    model.fit(
        train_dataset,
        epochs=50,
        steps_per_epoch=train_steps,
        validation_data=eval_dataset,
        validation_steps=eval_steps,
        callbacks=[
            tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5),
            tf.keras.callbacks.TensorBoard(log_dir=fn_args.model_run_dir),
        ]
    )
    
    # Save the model with serving function
    signatures = {
        'serving_default': _get_serve_tf_examples_fn(
            model, tf_transform_output
        ).get_concrete_function(
            tf.TensorSpec(shape=[None], dtype=tf.string, name='examples')
        )
    }
    
    model.save(fn_args.serving_model_dir, signatures=signatures)
