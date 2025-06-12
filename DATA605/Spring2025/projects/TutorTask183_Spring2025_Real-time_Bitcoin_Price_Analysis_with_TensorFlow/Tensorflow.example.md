# Real-Time Bitcoin Price Forecasting with TensorFlow

This project implements a real-time Bitcoin price prediction pipeline using LSTM-based deep learning. It showcases the full application of the API layer provided in `bitcoin_utils.py`, from data ingestion to model training and prediction.

This markdown describes the design decisions, implementation workflow, and results shown in the companion notebook: [`tensorflow.example.ipynb`](tensorflow.example.ipynb).


---

## Project Goals

The goal of this project is to:

- Collect live Bitcoin data via CoinGecko
- Engineer features for time series modeling
- Train and fine-tune an LSTM model
- Predict future prices in real time
- Power both static notebooks and live services (dashboard + scheduler)

---

## Workflow Summary

| Stage                       | Description |
|-----------------------------|-------------|
| Data Ingestion              | Load historical BTC prices from CSV, update with live data |
| Preprocessing               | Clean missing values, normalize, and remove anomalies |
| Feature Engineering         | Compute returns, SMAs, volatility, and lag features |
| Sequence Generation         | Convert to LSTM-compatible time windows |
| Model Training              | Train LSTM with early stopping |
| Fine-Tuning                 | Update model with recent market data |
| Prediction & Visualization  | Predict next price and plot against history |

---

## Design Decisions

### Why LSTM?

LSTM was selected because:

- Time series data like Bitcoin prices have long-term dependencies
- LSTM mitigates vanishing gradients better than standard RNNs
- It is widely used in financial modeling and forecasting

Model architecture:
- LSTM(128) → Dropout(0.4)
- LSTM(48) → Dropout(0.2)
- Dense(1) with MSE loss

---

### Feature Selection
Feature choices were based on technical indicators relevant in financial analysis:

| Feature                         | Purpose                          |
|------------------------------   |----------------------------------|
| `returns`                       | Captures price momentum          |
| `SMA_7`, `SMA_30`               | Short/medium trend tracking      |
| `volatility_7`, `volatility_30` | Measures risk                    |
| `lag_1day`                      | Introduces recency context       |
| `price`                         | The target for prediction        |

---

###  Anomaly Detection

We included robust anomaly filtering to improve model quality:

- Uses Z-score filtering with configurable threshold
- Removes price points beyond `|z| > 3.0`
- Controlled via `remove_anomalies=True` flag

---

###  Real-Time Update Strategy

Rather than retraining the model from scratch:

- We fine-tune using the latest 100 sequences
- This is done via the `fine_tune_model()` function
- Scheduler (`btc_scheduler.py`) runs this every 5 minutes

This makes the system lightweight and production-ready.

---

##  Results

- Smooth convergence of training and validation loss
- Predictions align well with recent market trends
- Final model is saved as `models/final_lstm_model.h5`

**Example Output**:

 Predicted Next Price: $90,300.85
