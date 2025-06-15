
import streamlit as st
import time
import pickle
from collections import deque
from bitcoin_forecast_utils import get_bitcoin_price_with_retry, build_rolling_features
from river import linear_model, metrics, preprocessing

# App Config
st.set_page_config(page_title="Bitcoin Forecasting with River", page_icon=":chart_with_upwards_trend:")
st.title("📈 Real-Time Bitcoin Price Forecasting using River")

# Load or initialize model with normalization
if "model" not in st.session_state:
    scaler = preprocessing.StandardScaler()
    regressor = linear_model.LinearRegression()
    st.session_state.model = scaler | regressor
    st.session_state.metric = metrics.MAE()
    st.session_state.rolling_prices = deque(maxlen=5)
    st.session_state.price_log = []

model = st.session_state.model
metric = st.session_state.metric
rolling_prices = st.session_state.rolling_prices
price_log = st.session_state.price_log

# Fetch live price
if st.button("🔄 Refresh BTC Price"):
    get_bitcoin_price_with_retry.cache_clear()
    st.rerun()

try:
    current_price = get_bitcoin_price_with_retry()
    st.metric("📌 Current BTC Price (USD)", f"${current_price:,.2f}")
except Exception as e:
    st.error(f"Failed to fetch price: {e}")
    st.stop()

# Update rolling window
rolling_prices.append(current_price)

# Predict only if enough data is available
if len(rolling_prices) == rolling_prices.maxlen:
    features = build_rolling_features(rolling_prices)
    pred_price = model.predict_one(features)

    # Display prediction
    # TEMP FIX: Add predicted delta to current price
    prediction = model.predict_one(features)
    corrected_prediction = current_price + prediction
    st.subheader("🧠 Predicted Next Price")
    st.success(f"${corrected_prediction:,.2f}")


    # Train model
    model.learn_one(features, current_price)
    metric = metric.update(current_price, pred_price)
    st.session_state.metric = metric

    # Log data
    price_log.append((current_price, pred_price))

# Optional: Show model weights
if st.checkbox("🔍 Show Model Weights"):
    try:
        weights = dict(model[-1].weights)
        st.json(weights)
        st.line_chart(list(weights.values()))
    except Exception as e:
        st.error("Could not display weights: " + str(e))

# Optional: Display log chart
if price_log:
    import pandas as pd
    df = pd.DataFrame(price_log, columns=["Actual", "Predicted"])
    st.line_chart(df)

