# Bitcoin Price Forecasting API

## Overview

The **Bitcoin Price Forecasting API** provides real-time predictions of Bitcoin prices based on historical data and a set of derived features. The system employs a **TensorFlow** model, trained using **LSTM (Long Short-Term Memory)** networks to predict future Bitcoin prices. The model is served using **TensorFlow Serving** via a Flask API, which can be accessed through HTTP.

The API interacts with external data sources, such as **CoinGecko**, **CoinCap**, and **Binance**, to gather historical Bitcoin price data. It processes this data with **TensorFlow Transform (TFT)** for feature engineering, including the generation of cyclic time features (hour and day of week) and volatility features (price change, rolling mean, etc.).

---

## API Components

### Data Fetching & Preprocessing

* The system fetches historical Bitcoin price data from public APIs: **CoinGecko**, **CoinCap**, or **Binance**. The data is processed using **TensorFlow Transform (TFT)**, which normalizes the data, handles missing values, and adds additional features such as cyclical time features (hour, day of the week) and volatility features based on price changes.

* **Preprocessing Details**:

  * **Normalization**: Normalizes Bitcoin price using Z-score normalization.
  * **Cyclical Time Features**: Converts hour and day of week into cyclical features using sine and cosine.
  * **Volatility Features**: Creates volatility-related features such as price change and rolling mean.

### Model Training

The model is trained using the **LSTM** (Long Short-Term Memory) architecture to capture time dependencies in Bitcoin prices. The model is trained on the processed features and predicts the future price of Bitcoin.

* **Model Architecture**:

  * **LSTM Layers**: To capture temporal dependencies in the Bitcoin price data.
  * **Dense Layers**: For learning complex patterns from the transformed features.
  * **Dropout**: To avoid overfitting during training.
  * **Loss Function**: **Mean Squared Error (MSE)** is used for regression tasks.

```python
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(WINDOW_SIZE, 1)),
    tf.keras.layers.LSTM(128, return_sequences=True),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.LSTM(64, return_sequences=False),
    tf.keras.layers.Dropout(0.2),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(1)
])
```

### Model Deployment

The trained model is deployed using **TensorFlow Serving**, which exposes the model through an HTTP API endpoint. The model is served with a **`serving_default`** signature that accepts serialized **`tf.train.Example`** input data and returns predictions.

---

## API Endpoint

### Model Prediction

* **Endpoint**: `/v1/models/bitcoin_model:predict`

* **Method**: `POST`

* **Input Format**: JSON

* **Input Payload Example**:

  ```json
  {
    "instances": [
      {
        "price": 45000,
        "hour": 12,
        "day_of_week": 1
      }
    ]
  }
  ```

  The input JSON includes the following fields:

  * `price`: The current Bitcoin price (float).
  * `hour`: The current hour of the day (integer).
  * `day_of_week`: The current day of the week (integer, where Monday = 0, Sunday = 6).

* **Response Format**:

  * The API returns a JSON object with the predicted Bitcoin price.
  * Example Response:

  ```json
  {
    "predicted_price": 45250.47
  }
  ```

---

## Model Serving Details

The model has been saved with the **`serving_default`** signature. It expects **serialized TensorFlow examples (`tf.train.Example`)** containing the following features:

* `price`: The current Bitcoin price (float).
* `hour`: The current hour (integer).
* `day_of_week`: The current day of the week (integer).

### TensorFlow Serving API Example

**URL**: `http://localhost:5000/v1/models/bitcoin_model:predict`

### Example Code for Prediction in Python

```python
import requests
import numpy as np

# Prepare input data
input_data = {
    "instances": [
        {
            "price": 45000,
            "hour": 12,
            "day_of_week": 1
        }
    ]
}

# Send POST request to model server
url = "http://localhost:5000/v1/models/bitcoin_model:predict"
response = requests.post(url, json=input_data)

# Handle and display the prediction
if response.status_code == 200:
    prediction = response.json()  # Get the model prediction
    print(f"Predicted Bitcoin Price: {prediction}")
else:
    print(f"Error: {response.status_code}")
    print(f"Response content: {response.content}")
```

---

## Model Training Pipeline

The model is trained using the **TFX pipeline**. The following components are part of the pipeline:

1. **CsvExampleGen**: Loads the data and splits it into training and evaluation datasets.
2. **StatisticsGen**: Generates statistics from the dataset.
3. **SchemaGen**: Infers the schema of the dataset.
4. **ExampleValidator**: Validates the dataset based on the inferred schema.
5. **Transform**: Applies feature transformations like scaling and generating new features (e.g., cyclical hour/day features, price volatility).
6. **Trainer**: The **LSTM** model is trained on the transformed dataset.
7. **Pusher**: Pushes the trained model to the serving directory for deployment.

### **Pipeline Code** (Simplified)

```python
import os
from tfx.orchestration import pipeline
from tfx.components import (
    CsvExampleGen, StatisticsGen, SchemaGen, ExampleValidator, Transform, 
    Trainer, Pusher
)

# Define pipeline components
example_gen = CsvExampleGen(input_base=_data_root)
statistics_gen = StatisticsGen(examples=example_gen.outputs['examples'])
schema_gen = SchemaGen(statistics=statistics_gen.outputs['statistics'])
example_validator = ExampleValidator(statistics=statistics_gen.outputs['statistics'], schema=schema_gen.outputs['schema'])
transform = Transform(examples=example_gen.outputs['examples'], schema=schema_gen.outputs['schema'], module_file=_module_file_transform)
trainer = Trainer(module_file=_module_file_trainer, examples=transform.outputs['transformed_examples'])
pusher = Pusher(model=trainer.outputs['model'], push_destination=pusher_pb2.PushDestination(filesystem=pusher_pb2.PushDestination.Filesystem(base_directory=_serving_model_dir)))

# Return the pipeline object
return pipeline.Pipeline(
    pipeline_name=_pipeline_name,
    components=[example_gen, statistics_gen, schema_gen, example_validator, transform, trainer, pusher]
)
```

---

## Model Details

The model uses **LSTM** layers to forecast Bitcoin prices. The architecture has been designed to handle time-series data with dependencies over 24-hour windows, which is the most common observation period for Bitcoin price forecasting.

* **Loss Function**: Mean Squared Error (MSE) is used to minimize prediction error during training.
* **Optimizer**: Adam optimizer with a learning rate of 0.001.

---

## Data Preprocessing with TensorFlow Transform (TFT)

The **preprocessing\_fn** function transforms the raw data to ensure it is in a format suitable for training. The preprocessing steps include:

1. **Price Normalization**: The `price` feature is normalized using Z-score.
2. **Cyclical Features**: The `hour` and `day_of_week` features are converted to **cyclical features** using sine and cosine.
3. **Volatility Features**: The `price_change` feature is computed, and volatility-related features are added.
4. **Missing Data Handling**: Missing values are replaced with zeros.

```python
def preprocessing_fn(inputs):
    price = _fill_in_missing(inputs.get(PRICE_KEY))
    outputs[TRANSFORMED_PRICE_KEY] = tft.scale_to_z_score(price)
    
    if 'hour' in inputs:
        hour = tf.cast(inputs['hour'], tf.float32)
        outputs['hour_sin'] = tf.sin(2 * np.pi * hour / 24.0)
        outputs['hour_cos'] = tf.cos(2 * np.pi * hour / 24.0)
    
    return outputs
```

---

## Conclusion

This API provides an end-to-end solution for Bitcoin price forecasting. By leveraging **TensorFlow**, **TensorFlow Transform**, and **TFX**, it allows for accurate predictions based on historical price data. The model is served via **TensorFlow Serving** and can be accessed via HTTP requests.

---
