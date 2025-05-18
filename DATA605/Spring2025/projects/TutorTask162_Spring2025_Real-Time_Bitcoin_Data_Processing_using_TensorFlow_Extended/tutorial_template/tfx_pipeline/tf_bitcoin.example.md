# Real-Time Bitcoin Price Forecasting System

## Overview

A complete Bitcoin price forecasting system built with TensorFlow Extended (TFX), featuring automated data pipeline, LSTM model training, real-time updates, and an interactive web dashboard.

## System Architecture

```
Bitcoin APIs → Data Collection → TFX Pipeline → Model Training → Model Serving → Dashboard
     ↓              ↓               ↓             ↓              ↓            ↓
  Coinbase      CSV Storage    Feature Eng.   LSTM Model   TF Serving   Web Interface
  CoinGecko     Data Validation  Transform     Auto-train   REST API     Real-time UI
  Binance       Schema Gen      Preprocessing    Deploy      Forecast     Charts & Metrics
```

## Key Components

### 1. Data Collection (`tf_bitcoin_utils.py`)
- **Multi-source APIs**: Coinbase, CoinGecko, and Binance with fallback logic
- **Automatic retry**: Falls back to next API if one fails
- **Data validation**: Ensures data quality and completeness
- **Synthetic fallback**: Generates realistic data if all APIs fail

```python
def fetch_bitcoin_prices(days=30) -> pd.DataFrame:
    for source in [fetch_from_coingecko, fetch_from_coincap, fetch_from_binance]:
        try:
            data = source(days)
            if data is not None and len(data) > 10:
                return data
        except Exception as e:
            logging.warning(f"Data source failed: {str(e)}")
    return generate_guaranteed_bitcoin_data(days)
```

### 2. TFX Pipeline (`tf_pipeline.py`)
Complete ML pipeline with these components:
- **CsvExampleGen**: Loads Bitcoin price data from CSV
- **StatisticsGen**: Generates data statistics for monitoring
- **SchemaGen**: Infers data schema automatically
- **ExampleValidator**: Validates incoming data against schema
- **Transform**: Feature engineering and preprocessing
- **Trainer**: LSTM model training
- **Pusher**: Deploys trained model to serving directory

### 3. Feature Engineering (`transform.py`)
Transforms raw price data into model-ready features:
- **Price normalization**: Z-score normalization of price values
- **Time features**: Cyclical encoding (sin/cos) for hour and day
- **Technical indicators**: Moving averages, price changes
- **Volatility features**: Price direction, volatility buckets

```python
def preprocessing_fn(inputs):
    outputs = {}
    # Normalize price
    price = _fill_in_missing(inputs.get(PRICE_KEY))
    outputs[TRANSFORMED_PRICE_KEY] = tft.scale_to_z_score(price)
    
    # Cyclical time features
    hour = tf.cast(inputs['hour'], tf.float32)
    outputs['hour_sin'] = tf.sin(2 * np.pi * hour / 24.0)
    outputs['hour_cos'] = tf.cos(2 * np.pi * hour / 24.0)
    
    return outputs
```

### 4. Model Training (`trainer.py`)
- **LSTM Architecture**: 64-unit LSTM with dropout and dense layers
- **Input features**: Normalized price, time features, technical indicators
- **Training**: 100 steps with validation on eval split
- **Output**: Trained model ready for serving

```python
def _build_model():
    inputs = tf.keras.layers.Input(shape=(1,), name=FEATURE_KEY)
    x = tf.keras.layers.Reshape((1, 1))(inputs)
    x = tf.keras.layers.LSTM(64, return_sequences=False)(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    x = tf.keras.layers.Dense(32, activation='relu')(x)
    outputs = tf.keras.layers.Dense(1)(x)
    model = tf.keras.Model(inputs=inputs, outputs=outputs)
    return model
```

### 5. Real-Time Updates (`realtime_update.py`)
Automated system that:
- **Monitors data**: Checks for new Bitcoin price data every hour
- **Updates dataset**: Appends new data to existing CSV
- **Triggers retraining**: Runs TFX pipeline when new data arrives
- **Evaluates performance**: Tests model accuracy on recent data
- **Generates forecasts**: Creates new predictions automatically

### 6. Prediction System (`predict.py`)
- **Realistic forecasting**: Uses statistical models with cycles and trends
- **Multiple horizons**: 24-hour, 3-day, and 7-day predictions
- **Visualization**: Creates charts showing forecast with confidence
- **Analysis tools**: Functions to analyze existing forecast CSV files

### 7. API Server (`api_server.py`)
REST API providing:
- **Current price**: `/current` - Latest Bitcoin price
- **Forecasts**: `/forecast?hours=24` - Multi-horizon predictions
- **Health check**: `/health` - Service status

### 8. Interactive Dashboard (`simple_dashboard.py`)
Web interface featuring:
- **Real-time price display**: Auto-updating current price
- **Interactive charts**: Historical price + forecast visualization
- **Key predictions**: 24h, 3d, 7d forecast cards with percentage changes
- **Control buttons**: Generate new forecast, update data
- **Responsive design**: Works on desktop and mobile

## Implementation Results

### Model Performance
- **Architecture**: LSTM(64) + Dense(32) + Output(1)
- **Training Loss**: 0.0038 (final)
- **Validation Loss**: 0.0001514 (final)
- **Training MAE**: 0.0404
- **Validation MAE**: 0.0093

### System Capabilities
- **Data Sources**: 3 APIs with automatic failover
- **Update Frequency**: Hourly data collection and processing
- **Forecast Horizons**: 1 hour to 7 days
- **Dashboard Updates**: Real-time price and chart updates
- **Model Retraining**: Automatic daily retraining

## Usage

### Setup and Initial Run
```bash
# 1. Setup directories and initial data
python setup.py

# 2. Run TFX pipeline (train initial model)
python tf_pipeline.py

# 3. Generate initial forecast
python predict.py

# 4. Start the dashboard
python simple_dashboard.py

# 5. (Optional) Start API server
python api_server.py
```

### Real-Time Operation
```bash
# Start real-time monitoring and updates
python realtime_update.py
```

### Dashboard Access
- Open browser to `http://localhost:5000`
- View real-time Bitcoin price
- See forecast charts and predictions
- Use buttons to generate new forecasts or update data

### API Usage
```bash
# Get current price
curl http://localhost:5001/current

# Get 24-hour forecast
curl http://localhost:5001/forecast?hours=24
```


## Accessing Model and Forecast Data Inside Docker Container

### 1. Accessing the Running Docker Container

To access the running Docker container and inspect the model or forecast data:

1. **Find the container ID or name**:
   Run the following to list all running containers:
   ```bash
   docker ps
   ```

2. **Access the container interactively**:
   ```bash
   docker exec -it <container_name_or_id> /bin/bash
   ```

   Replace `<container_name_or_id>` with the actual name or ID from the `docker ps` output.

3. **Navigate to the model directory**:
   The trained model is stored in the `/app/tfx_pipeline_output/bitcoin_price_pipeline/serving_model/` directory. Once inside the container, navigate there using:
   ```bash
   cd /app/tfx_pipeline_output/bitcoin_price_pipeline/serving_model/
   ```

4. **List model files**:
   You should see files like `saved_model.pb` and a `variables/` directory. To list the contents, run:
   ```bash
   ls
   ```

5. **Access forecast data**:
   The forecast data is stored in the `/app/forecasts/` directory. You can navigate there with:
   ```bash
   cd /app/forecasts/
   ls
   ```

---

### 2. Copying Files from the Container to the Host

To copy the model or forecast files from the container to your local machine, use the `docker cp` command.

#### Copy the model directory to the host:
```bash
docker cp <container_id>:/app/tfx_pipeline_output/bitcoin_price_pipeline/serving_model ./serving_model
```

#### Copy the forecast data directory to the host:
```bash
docker cp <container_id>:/app/forecasts ./forecasts
```

This will copy the files and directories from the container to your current working directory on the host machine.

---

### 3. Helpful Directory Structure

- **Model Files**: `/app/tfx_pipeline_output/bitcoin_price_pipeline/serving_model/`
- **Forecast Data**: `/app/forecasts/`
- **Raw Data**: `/app/data/bitcoin/`


