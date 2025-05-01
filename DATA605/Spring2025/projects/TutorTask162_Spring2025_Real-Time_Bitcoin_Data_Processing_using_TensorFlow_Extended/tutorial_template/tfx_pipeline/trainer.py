import tensorflow as tf
import tensorflow_transform as tft
from tfx_bsl.public import tfxio
from tfx.components.trainer.fn_args_utils import FnArgs


FEATURE_KEY = 'normalized_price'
LABEL_KEY = 'normalized_price'  

def _input_fn(file_pattern, data_accessor, schema, batch_size=32) -> tf.data.Dataset:
    """Creates a dataset from transformed data.
    
    Args:
        file_pattern: Input file pattern for transformed TFRecords
        data_accessor: DataAccessor for reading TFRecords
        schema: Schema of the transformed data
        batch_size: Batch size for training
        
    Returns:
        A tf.data.Dataset containing features and labels
    """
    raw_dataset = data_accessor.tf_dataset_factory(
        file_pattern,
        tfxio.TensorFlowDatasetOptions(batch_size=batch_size),
        schema=schema
    )

    def _debug_keys(features):
        tf.print("DEBUG - Available feature keys:", list(features.keys()))
        return features
    
    def _extract_features_and_label(features):
        if not features:
            tf.print("WARNING: Empty features dictionary received")
        
        if FEATURE_KEY not in features:
            raise KeyError(f"Feature key '{FEATURE_KEY}' not found in available keys: {list(features.keys())}")
        
        feature_tensor = features[FEATURE_KEY]
        
        feature_dict = {FEATURE_KEY: feature_tensor}
        
        tf.print("Feature shape:", tf.shape(feature_tensor))
        
        return feature_dict, feature_tensor  

    return raw_dataset.map(_debug_keys).map(_extract_features_and_label)


def _build_keras_model():
    """Builds a simple LSTM-based Keras model for time series forecasting."""
    inputs = tf.keras.layers.Input(shape=(1,), name=FEATURE_KEY)
    
    x = tf.keras.layers.Dense(64, activation='relu')(inputs)
    x = tf.keras.layers.Dense(32, activation='relu')(x)
    outputs = tf.keras.layers.Dense(1)(x)  
    
    model = tf.keras.Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    
    model.summary()
    
    return model


def run_fn(fn_args: FnArgs):
    """Train the model using the given arguments."""
    transform_output = tft.TFTransformOutput(fn_args.transform_output)
    
    tf.print("Transformed features spec:", transform_output.transformed_feature_spec())

    model = _build_keras_model()

    train_dataset = _input_fn(
        fn_args.train_files,
        fn_args.data_accessor,
        schema=transform_output.transformed_metadata.schema,
        batch_size=32
    )
    
    eval_dataset = _input_fn(
        fn_args.eval_files,
        fn_args.data_accessor,
        schema=transform_output.transformed_metadata.schema,
        batch_size=32
    )

    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5)
    ]

    model.fit(
        train_dataset,
        steps_per_epoch=fn_args.train_steps,
        validation_data=eval_dataset,
        validation_steps=fn_args.eval_steps,
        callbacks=callbacks,
        verbose=2
    )

    model.save(fn_args.serving_model_dir, save_format='tf')

    print("✅ Model training and saving completed successfully.")