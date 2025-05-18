# Real-Time Bitcoin Price Forecasting with TensorFlow

This project implements a real-time Bitcoin price prediction pipeline using LSTM-based deep learning. It showcases the full application of the API layer provided in `bitcoin_utils.py`, from data ingestion to model training and prediction.

This markdown describes the design decisions, implementation workflow, and results shown in the companion notebook: [`tensorflow.example.ipynb`](tensorflow.example.ipynb).

---

## 🎯 Objective

The goal is to build a time series modeling system that:

- Fetches live Bitcoin price data from CoinGecko
- Processes and cleans the dataset with anomaly detection
- Extracts relevant financial indicators
- Trains an LSTM model to predict the next day's price
- Supports real-time model fine-tuning and inference

---

## 🏗️ Pipeline Overview

### ✅ Step 1: Data Loading & Real-Time Update

- Loads historical data from `btc-usd-max.csv`
- Automatically fetches the latest price via the CoinGecko API using `update_dataset_with_latest()`
- Uses `load_and_clean_csv()` to sanitize timestamps, enforce types, and optionally filter anomalies

### ✅ Step 2: Exploratory Data Analysis (EDA)

The notebook includes key EDA plots to visualize:

- Raw price trends (linear + log scale)
- Relationship between price and market cap
- Moving averages (30-day, 90-day) to highlight trend direction

These plots guide our feature selection and show how Bitcoin’s market behavior evolves over time.

### ✅ Step 3: Feature Engineering

Using `technical_features()` we add:

- Daily returns
- SMA (7 and 30-day)
- Rolling volatility
- Lagged prices

These are used to generate multivariate sequences with `generate_sequences()`.

---

## 🧠 Modeling Approach

### Model Type: LSTM (Long Short-Term Memory)

We chose LSTM over traditional RNNs or simple autoregressive models due to its ability to:

- Capture long-term dependencies in time series
- Handle high volatility and non-stationarity
- Generalize well in financial prediction tasks

The model uses:

- Two LSTM layers (`128`, `48` units) with dropout
- Mean squared error loss
- Adam optimizer

Training is done using `train_lstm_model()` with early stopping on validation loss.

---

## ⚙️ Fine-Tuning and Real-Time Inference

- Once the model is saved as `models/final_lstm_model.h5`, it can be reused by the scheduler or dashboard.
- We demonstrate how to fine-tune the model on the last 100 sequences with `fine_tune_model()` to adapt to new market conditions.
- Finally, we use `predict_next_price()` to generate the next Bitcoin price and plot it against the last 60 prices.

---

## 📈 Results

- The model captures Bitcoin's general price trend with reasonable prediction quality.
- Training/validation losses show good convergence without overfitting.
- Predicted next price is plotted against recent prices to visually confirm model behavior.

Example output:$90,300.85   

---

## 🧠 Key Takeaways

- The modular design allows easy integration with Streamlit dashboards or schedulers.
- The utility layer simplifies the complex workflow of live data ingestion and deep learning.
- Anomaly filtering improves robustness against API noise or missing data.

---

## 🔗 References

- `tensorflow.example.ipynb`: Full demo notebook
- `bitcoin_utils.py`: Core utility module
- [CoinGecko API](https://www.coingecko.com/en/api)
- [TensorFlow LSTM Docs](https://www.tensorflow.org/api_docs/python/tf/keras/layers/LSTM)

---
