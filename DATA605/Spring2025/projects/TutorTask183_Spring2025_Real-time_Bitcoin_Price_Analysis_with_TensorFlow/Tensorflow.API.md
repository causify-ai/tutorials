# 🧠 TensorFlow API Layer for Real-Time Bitcoin Price Prediction

This document describes the utility API implemented in `bitcoin_utils.py`, which wraps TensorFlow and CoinGecko into a modular, reusable system for time series modeling. It powers both our Jupyter workflows and real-time components like the scheduler and dashboard.

---

## 🚀 Why Build This API Layer?

The goal was to abstract away boilerplate and standardize the data and modeling pipeline. While native libraries (e.g., TensorFlow, requests, Keras) are powerful, using them directly creates fragmented code and limited reusability.

Our `bitcoin_utils.py` solves this by:

- Encapsulating logic for I/O, transformation, and modeling
- Supporting real-time fine-tuning with live data
- Enabling fast experimentation through Jupyter + deployment via Streamlit

---

## 🧰 API Overview: `bitcoin_utils.py`

| Function                       | Description |
|--------------------------------|-------------|
| `load_and_clean_csv()`         | Reads CSV, parses datetime, removes anomalies (optional Z-score filtering) |
| `update_dataset_with_latest()` | Queries CoinGecko for the newest price and appends if new |
| `technical_features()`         | Adds `returns`, SMAs, volatility bands, and lags |
| `generate_sequences()`         | Transforms features into `(X, y)` LSTM-ready sequences |
| `build_lstm_model()`           | Builds a 2-layer LSTM with dropout |
| `train_lstm_model()`           | Trains the LSTM with early stopping |
| `tune_lstm_model()`            | (Optional) Runs KerasTuner to optimize model architecture |
| `fine_tune_model()`            | Updates a pretrained model using recent sequences |
| `predict_next_price()`         | Predicts the next value and plots vs. history |
| `plot_training_loss()`         | Visualizes model training and validation loss |

---

## 🧠 Design Decisions

### 📈 Why LSTM?

LSTM is used instead of vanilla RNN or CNN because:

- Bitcoin pricing is **non-stationary and autocorrelated**
- LSTMs maintain long-term memory across timesteps
- They’re resilient to gradient vanishing (vs RNN)

We used:
- Two LSTM layers: 128 → 48 units
- Dropout for regularization
- MSE loss with Adam optimizer

---

### 🧪 Feature Design

We selected features based on **technical indicators** commonly used in financial modeling:

- `returns`: Captures momentum
- `SMA_7`, `SMA_30`: Trend strength
- `volatility_7`, `volatility_30`: Market uncertainty
- `lag_1day`: Recent context
- `price`: The core prediction target

These were chosen for interpretability, signal quality, and efficiency.

---

### 🚨 Anomaly Filtering

Live APIs can return noisy or erroneous data. We use:

- Z-score thresholding on price
- Configurable filtering in `load_and_clean_csv()`
- Toggle via `remove_anomalies=True`

This improves model robustness for real-time inference.

---

### 🔁 Real-Time Strategy

Instead of full retraining, we use:

- Lightweight fine-tuning via `fine_tune_model()`
- Performed on the latest N sequences (e.g., 100)
- Integrated into a live scheduler for updates every 5 minutes

This design makes the model suitable for production-style inference with minimal overhead.

---

## 🧪 Optional: Hyperparameter Tuning

The module supports tuning with KerasTuner (`tune_lstm_model()`):

- Layer sizes
- Dropout rates
- Early stopping
- Trial counts

We comment this section in notebooks to preserve runtime simplicity — but it’s valuable for optimizing production models.

---

## 🖥️ API in Action

The API is consumed by:

- ✅ `tensorflow.API.ipynb` — Basic usage examples
- ✅ `tensorflow.example.ipynb` — Full model training and evaluation
- ✅ `btc_scheduler.py` — Live update + predict loop
- ✅ `btc_dashboard.py` — Streamlit UI calling prediction utilities

---

## ⚙️ Abstraction Strategy

We designed the API to be:

- **Thin notebooks** — Easy to follow and modify
- **Reusable** — Shared logic for Streamlit, CLI, and scheduler
- **Maintainable** — New features or changes only require updates in `bitcoin_utils.py`

---

## 📁 References

- 📄 [`bitcoin_utils.py`](./bitcoin_utils.py)
- 📓 [`tensorflow.API.ipynb`](./tensorflow.API.ipynb)
- [TensorFlow LSTM Layer](https://www.tensorflow.org/api_docs/python/tf/keras/layers/LSTM)
- [CoinGecko API](https://www.coingecko.com/en/api)
- [KerasTuner Docs](https://keras.io/keras_tuner/)
