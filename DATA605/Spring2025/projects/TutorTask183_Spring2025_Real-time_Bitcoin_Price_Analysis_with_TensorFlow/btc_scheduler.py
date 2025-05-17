# btc_scheduler.py
# Real-time Bitcoin prediction scheduler (every 5 minutes)

from apscheduler.schedulers.blocking import BlockingScheduler
from bitcoin_utils import (
    update_dataset_with_latest,
    load_and_clean_csv,
    technical_features,
    generate_sequences,
    fine_tune_model
)
from tensorflow.keras.models import load_model
import pandas as pd
import numpy as np
import os
from datetime import datetime

# Configuration
CSV_PATH = "btc-usd-max.csv"
MODEL_PATH = "models/final_lstm_model.h5"
FEATURES = ["price", "returns", "SMA_7", "SMA_30", "volatility_7", "volatility_30", "lag_1day"]
WINDOW_SIZE = 60
LOG_PATH = "btc_predictions_log.csv"

def update_and_predict():
    print("\n⏱️ Running scheduled update at:", datetime.utcnow())

    # Step 1: Update the dataset
    update_dataset_with_latest(CSV_PATH)

    # Step 2: Load updated dataset
    df = load_and_clean_csv(CSV_PATH)
    df = technical_features(df)
    df = df.dropna(subset=FEATURES + ["price"])

    # Step 3: Generate sequences
    X, y, scaler_X, scaler_y = generate_sequences(df, FEATURES, target="price", window_size=WINDOW_SIZE)

    # Step 4: Load and fine-tune model on last 500 examples
    model = fine_tune_model(MODEL_PATH, X[-500:], y[-500:], epochs=3)

    # Step 5: Predict the next price
    latest_input = X[-1].reshape(1, X.shape[1], X.shape[2])
    y_pred_scaled = model.predict(latest_input)
    y_pred = scaler_y.inverse_transform(y_pred_scaled)
    pred_price = float(y_pred[0][0])

    print(f"\U0001F4C8 Predicted BTC price: ${pred_price:,.2f}")

    # Step 6: Log the prediction
    log_entry = pd.DataFrame({
        "timestamp": [datetime.utcnow().isoformat()],
        "predicted_price": [pred_price]
    })
    log_entry.to_csv(LOG_PATH, mode="a", header=not os.path.exists(LOG_PATH), index=False)

# Scheduler setup
scheduler = BlockingScheduler()
scheduler.add_job(update_and_predict, "interval", minutes=5)

print("✅ Scheduler started. Predicting every 5 minutes...")
scheduler.start()
