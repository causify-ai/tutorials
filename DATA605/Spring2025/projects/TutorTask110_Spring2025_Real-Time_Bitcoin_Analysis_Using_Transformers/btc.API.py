"""
Real-time Bitcoin price prediction using a Transformer model, served via Streamlit.

1. Citations:
   - Vaswani et al., “Attention is All You Need” (https://arxiv.org/abs/1706.03762)
   - CryptoCompare API (https://min-api.cryptocompare.com/)
   - PyTorch (https://pytorch.org/)
   - Streamlit (https://streamlit.io/)
   - TA-Lib (https://technical-analysis-library-in-python.readthedocs.io/)

2. Run code linters like `black` and `pylint` to enforce consistency with coding standards.

3. Full documentation available at: btc.API.md

Follow the coding style guide:
https://github.com/causify-ai/helpers/blob/master/docs/coding/all.coding_style.how_to_guide.md
"""

import streamlit as st
import pandas as pd
import numpy as np
import torch
import requests
import joblib
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from utils.model import MultiStepTransformer
import altair as alt
import pytz
from dotenv import load_dotenv
import ta
import os

# === Setup ===
load_dotenv()
SESSION_DIR = "database/session_data"
os.makedirs(SESSION_DIR, exist_ok=True)

# === Device ===
device = (
    torch.device("cuda") if torch.cuda.is_available()
    else torch.device("mps") if torch.backends.mps.is_available()
    else torch.device("cpu")
)

# === Load model + scaler ===
scaler = joblib.load("utils/saved_models/30step_scaler.pkl")
model = MultiStepTransformer(input_dim=scaler.n_features_in_)
state_dict = torch.load("utils/saved_models/30step_transformer.pth", map_location=device, weights_only=True)
model.load_state_dict(state_dict)
model.to(device)
model.eval()

# === Helper ===
def get_latest_btc_data(api_key, limit=30):
    url = "https://min-api.cryptocompare.com/data/v2/histominute"
    params = {"fsym": "BTC", "tsym": "USD", "limit": limit - 1, "api_key": api_key}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return pd.DataFrame()
    data = response.json()['Data']['Data']
    df = pd.DataFrame(data)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    df = df[["time", "close", "volumefrom"]].rename(columns={"close": "Close", "volumefrom": "Volume"})
    df["log_return"] = np.log(df["Close"] / df["Close"].shift(1)).fillna(0)
    df["ma_5"] = df["Close"].rolling(window=5).mean().bfill()
    df["rsi_14"] = ta.momentum.RSIIndicator(close=df["Close"], window=14).rsi().bfill()
    df["Volume"] = df["Volume"].bfill()
    return df[["time", "Close", "log_return", "ma_5", "rsi_14", "Volume"]].dropna().reset_index(drop=True)

def predict_price(prices, n_steps=30, clip_pct=0.02):
    input_df = prices.copy()
    if hasattr(scaler, "feature_names_in_") and len(scaler.feature_names_in_) == input_df.shape[1]:
        input_df.columns = scaler.feature_names_in_
    scaled = scaler.transform(input_df)
    x = torch.tensor(scaled, dtype=torch.float32).unsqueeze(0).to(device)
    with torch.no_grad():
        pred_scaled_seq = model(x).squeeze().cpu().numpy()
    preds = []
    last_price = input_df["Close"].iloc[-1]
    for pred_scaled in pred_scaled_seq:
        dummy = np.zeros((1, scaler.n_features_in_))
        dummy[0, 0] = pred_scaled
        pred_price = scaler.inverse_transform(dummy)[0][0]
        pred_price = np.clip(pred_price, last_price * (1 - clip_pct), last_price * (1 + clip_pct))
        preds.append(pred_price)
        last_price = pred_price
    return preds

# === Streamlit UI ===
st.set_page_config("BTC Predictor", layout="wide")
st.title("🚀 Real-Time Bitcoin Price Prediction")
st.caption("Live BTC price + Transformer prediction every minute")
forecast_horizon = st.selectbox("🔮 Predict how many minutes ahead:", list(range(1, 31)), index=0)
st_autorefresh(interval=60_000, key="refresh")

API_KEY = os.getenv("CRYPTO_COMPARE_API_KEY")
df = get_latest_btc_data(API_KEY)
if len(df) < 30:
    st.warning("Not enough data (need 30 mins of 1-min BTC prices). Try again later.")
    st.stop()

actual_price = df["Close"].iloc[-1]
predicted_prices = predict_price(df.drop(columns=["time"]), forecast_horizon)
start_time = pd.to_datetime(df["time"].iloc[-1]).floor("min")
predicted_times = [start_time + pd.Timedelta(minutes=i+1) for i in range(forecast_horizon)]

session_key = f"hist_df_{forecast_horizon}"
session_file = os.path.join(SESSION_DIR, f"{session_key}.csv")
if session_key not in st.session_state:
    if os.path.exists(session_file):
        st.session_state[session_key] = pd.read_csv(session_file, parse_dates=["Time"])
    else:
        st.session_state[session_key] = pd.DataFrame(columns=["Time", "Actual", "Predicted"])

existing_df = st.session_state[session_key]
existing_df["Time"] = pd.to_datetime(existing_df["Time"]).dt.floor("min")
st.session_state[session_key] = existing_df

predicted_times_set = set(predicted_times)
st.session_state[session_key] = st.session_state[session_key][~(
    (st.session_state[session_key]["Time"].isin(predicted_times_set)) &
    (st.session_state[session_key]["Predicted"].notna())
)]

clean_df = st.session_state[session_key].copy()
if start_time not in clean_df["Time"].values:
    clean_df.loc[len(clean_df)] = [start_time, actual_price, np.nan]
for t, p in zip(predicted_times, predicted_prices):
    clean_df = clean_df[~((clean_df["Time"] == t) & (clean_df["Predicted"].notna()))]
    clean_df.loc[len(clean_df)] = [t, np.nan, p]
clean_df.drop_duplicates(subset=["Time", "Actual", "Predicted"], keep="last", inplace=True)
clean_df.sort_values("Time", inplace=True)
clean_df["Time"] = pd.to_datetime(clean_df["Time"]).dt.tz_localize(None)
one_hour_ago = pd.Timestamp.utcnow().replace(tzinfo=None)
clean_df = clean_df[clean_df["Time"] >= one_hour_ago]

st.session_state[session_key] = clean_df
clean_df.to_csv(session_file, index=False)

# === Metrics ===
delta_value = predicted_prices[0] - actual_price
delta_percent = (delta_value / actual_price) * 100
actual_deltas = st.session_state[session_key]["Actual"].dropna()
if len(actual_deltas) >= 2:
    previous_actual = actual_deltas.iloc[-2]
    actual_delta_value = actual_price - previous_actual
    actual_delta_percent = (actual_delta_value / previous_actual) * 100
else:
    actual_delta_value = 0
    actual_delta_percent = 0

col1, col2 = st.columns(2)
col1.metric("📈 Latest BTC Price", f"${actual_price:,.2f}", delta=f"{actual_delta_value:+.2f} ({actual_delta_percent:+.2f}%)")
if predicted_prices:
    predicted_price_final = predicted_prices[-1]
    col2.metric(f"🔮 Predicted +{forecast_horizon} min Price", f"${predicted_price_final:,.2f}", delta=f"{delta_value:+.2f} ({delta_percent:+.2f}%)")
else:
    st.error("Prediction failed — no values returned.")

# === Chart ===
hist_df = st.session_state[session_key].dropna(subset=["Actual", "Predicted"], how="all")
actual_hist = hist_df.dropna(subset=["Actual"]).rename(columns={"Actual": "Price"})
actual_hist["Type"] = "Actual"
live_actual = df.copy().rename(columns={"time": "Time", "Close": "Price"})
live_actual["Type"] = "Actual"
pred_hist = hist_df.dropna(subset=["Predicted"]).rename(columns={"Predicted": "Price"})
pred_hist["Type"] = "Predicted"
min_len = min(len(predicted_times), len(predicted_prices))
predicted_times = predicted_times[:min_len]
predicted_prices = predicted_prices[:min_len]

live_pred = pd.DataFrame({
    "Time": predicted_times,
    "Price": predicted_prices,
    "Type": ["Predicted"] * min_len
})

chart_df = pd.concat([actual_hist[["Time", "Price", "Type"]], live_actual[["Time", "Price", "Type"]], pred_hist[["Time", "Price", "Type"]], live_pred], ignore_index=True)
chart_df["Time"] = pd.to_datetime(chart_df["Time"]).dt.tz_localize("UTC").dt.tz_convert("US/Eastern")

prediction_start = pd.to_datetime(predicted_times[0]).tz_localize("UTC").tz_convert("US/Eastern")
prediction_end = pd.to_datetime(predicted_times[-1]).tz_localize("UTC").tz_convert("US/Eastern")
prediction_marker = alt.Chart(pd.DataFrame({"Time": [prediction_start]})).mark_rule(color="gray", strokeDash=[4, 4]).encode(x="Time:T")
shaded_region = alt.Chart(pd.DataFrame({"start": [prediction_start], "end": [prediction_end]})).mark_rect(opacity=0.1, fill="orange").encode(x="start:T", x2="end:T")

chart = alt.Chart(chart_df).mark_line(point=True).encode(
    x=alt.X("Time:T", title="Time (EST)", axis=alt.Axis(format="%H:%M:%S")),
    y=alt.Y("Price:Q", title="BTC Price (USD)", scale=alt.Scale(zero=False)),
    color=alt.Color("Type:N", title="Legend", scale=alt.Scale(domain=["Actual", "Predicted"], range=["#4e79a7", "#e15759"])),
    tooltip=[alt.Tooltip("Time:T", title="Time (EST)"), alt.Tooltip("Price:Q", title="BTC Price ($)", format=".2f"), alt.Tooltip("Type:N")]
).properties(title=f"📈 BTC Price: Actual + {forecast_horizon}-Minute Prediction", height=450).interactive()

st.altair_chart(shaded_region + chart + prediction_marker, use_container_width=True)
csv = chart_df.to_csv(index=False)
st.download_button(label="📅 Download Forecast Data as CSV", data=csv, file_name=f"btc_forecast_{forecast_horizon}min.csv", mime="text/csv")
st.caption("Data from CryptoCompare • Model inference via PyTorch Transformer")
