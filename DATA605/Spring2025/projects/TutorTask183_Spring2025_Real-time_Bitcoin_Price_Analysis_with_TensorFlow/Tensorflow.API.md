# TensorFlow API Layer Documentation

This document explains the software layer developed in `bitcoin_utils.py`, which provides a clean, modular interface on top of native APIs such as:

- **CoinGecko** (via REST API for real-time Bitcoin market data)
- **TensorFlow/Keras** (for LSTM-based time series modeling)
- **scikit-learn** (for data preprocessing)

---

## 🔧 Utility Module: `bitcoin_utils.py`

This Python module encapsulates the functionality needed to create a real-time Bitcoin price prediction pipeline. It abstracts complexity and makes the workflow reproducible and maintainable.

---

### 📂 Data Loading & Updating

#### `load_and_clean_csv(file_path: str, remove_anomalies=True)`
- Loads and cleans a historical dataset.
- Converts timestamps, enforces numeric types, handles NaNs, and drops duplicates.
- Optionally removes anomalies using Z-score filtering.

#### `update_dataset_with_latest(csv_path: str)`
- Fetches the most recent data point from the [CoinGecko API](https://www.coingecko.com/en/api/documentation).
- Appends it to the CSV if the timestamp is new.

---

### ⚙️ Feature Engineering

#### `technical_features(df: pd.DataFrame)`
- Adds:
  - Returns
  - Simple Moving Averages (7, 30)
  - Volatility (7, 30)
  - Lagged price (`lag_1day`)
  
#### `generate_sequences(df, features, target='price', window_size=60)`
- Converts time series into LSTM-compatible 3D sequences.
- Scales both features and target using `MinMaxScaler`.

---

### 🧠 Model Operations

#### `build_lstm_model(input_shape)`
- Returns a pre-configured 2-layer LSTM model with dropout.
- Uses Keras Sequential API.

#### `train_lstm_model(model, X_train, y_train, X_val, y_val)`
- Trains the model with early stopping on validation loss.

#### `fine_tune_model(model_path, X_recent, y_recent)`
- Loads a saved model and fine-tunes it on the latest input sequences.

#### `tune_lstm_model(...)`
- (Optional) Uses KerasTuner to optimize LSTM hyperparameters like units and dropout.

---

### 📉 Visualization

#### `plot_training_loss(history)`
- Plots training vs validation loss curves from the Keras training history.

---

### 📈 Prediction

#### `predict_next_price(model, X_input, scaler_y, recent_prices=None, plot=True)`
- Predicts the next Bitcoin price using the last input window.
- Optionally plots recent prices and the predicted value.

---

## 🌐 API Design Notes

- **Native APIs Used**:
  - CoinGecko for live data
  - TensorFlow/Keras for LSTM modeling
  - Matplotlib for visualization
- **Abstraction Goal**: Avoid inline implementation. All complexity is wrapped in callable, testable functions.
- **Design Philosophy**: Minimal logic in notebooks, maximal reusability from `bitcoin_utils.py`.

---

## 📁 References

- CoinGecko API Docs: https://www.coingecko.com/en/api/documentation
- TensorFlow LSTM: https://www.tensorflow.org/api_docs/python/tf/keras/layers/LSTM
- [Notebook Demo](tensorflow.API.ipynb)
