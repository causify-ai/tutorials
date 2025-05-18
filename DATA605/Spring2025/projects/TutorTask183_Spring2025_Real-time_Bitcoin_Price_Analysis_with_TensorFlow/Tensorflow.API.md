# TensorFlow API Layer Documentation

This document describes the software layer implemented in `bitcoin_utils.py`, which wraps around native APIs like CoinGecko and TensorFlow. It modularizes the data processing and modeling steps required to build a real-time Bitcoin price prediction system.

---

## 🔍 Project Motivation

The native APIs (CoinGecko, TensorFlow, Keras) offer powerful tools, but their raw usage involves repetitive code and loose structure. The wrapper functions in this module:

- Reduce boilerplate
- Enforce reproducibility
- Support real-time retraining and prediction
- Decouple implementation from experimentation

---

## 📦 Utility Overview: `bitcoin_utils.py`

This module defines a pipeline-friendly API with clean, reusable components:

| Function                        | Purpose                                               |
|---------------------------------|--------------------------------------------------------|
| `load_and_clean_csv()`          | Loads and sanitizes time series data                  |
| `update_dataset_with_latest()`  | Fetches new price data using CoinGecko API            |
| `technical_features()`          | Adds domain-relevant indicators (returns, SMA, etc.)  |
| `generate_sequences()`          | Prepares windowed, normalized sequences for LSTM      |
| `build_lstm_model()`            | Instantiates a 2-layer LSTM architecture              |
| `train_lstm_model()`            | Trains model with early stopping                      |
| `fine_tune_model()`             | Adapts the model to the latest data in real-time      |
| `predict_next_price()`          | Outputs next price + optional visualization           |
| `plot_training_loss()`          | Shows model learning curves                           |

---

## 🧠 Design Decisions & Logic

### 🧩 Why LSTM?
Bitcoin price prediction is a sequential task with temporal dependencies. LSTM (Long Short-Term Memory) networks are a natural fit:
- They retain memory across timesteps
- Outperform standard RNNs in long-horizon prediction
- Handle vanishing gradients better in deep networks

The model:
- Uses two LSTM layers with dropout
- Is pre-configured for real-time fine-tuning
- Accepts sequences of shape `(window_size, num_features)`

---

### 📊 Why These Features?
We chose features grounded in technical analysis:

- `returns`: Captures daily price momentum
- `SMA_7`, `SMA_30`: Highlight short- and medium-term trends
- `volatility_7`, `volatility_30`: Reflect short/long uncertainty
- `lag_1day`: Acts as a temporal anchor
- `price`: Original signal, retained for completeness

These were selected to balance signal strength with model simplicity.

---

### 🔍 Anomaly Detection Logic
Real-time data ingestion can lead to anomalies or API glitches. To prevent the model from learning on corrupted data:

- `load_and_clean_csv()` includes optional Z-score-based filtering
- Outliers above a configurable threshold (e.g., 3.0) are removed
- This is toggled via `remove_anomalies=True`

---

### 🔁 Real-Time Update Strategy
Instead of full retraining:
- The system uses `fine_tune_model()` on the latest N sequences
- This allows for lightweight, frequent updates with live data

---

### 🧪 Optional Hyperparameter Tuning
The `tune_lstm_model()` function wraps KerasTuner for reproducible optimization:
- Number of LSTM units
- Dropout rates
- Trial count + early stopping for fast convergence

This tuning is **optional** and was commented out in the demo for runtime reasons.

---

## 🔧 Abstraction Strategy

We chose to:

- Centralize all logic in `bitcoin_utils.py`
- Keep notebooks as thin, readable demos
- Maintain modularity for testing, debugging, and deployment

This ensures that:
- The dashboard, scheduler, and Jupyter demo all reuse the same core
- You can scale to other coins or timeframes by reusing this structure

---

## 📁 References

- CoinGecko API: https://www.coingecko.com/en/api
- TensorFlow LSTM: https://www.tensorflow.org/api_docs/python/tf/keras/layers/LSTM
- KerasTuner: https://keras.io/keras_tuner/
- Companion notebook: `tensorflow.API.ipynb`
