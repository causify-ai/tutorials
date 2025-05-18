# dashboard.py

import os
import time
import boto3
import streamlit as st
import pandas as pd
import numpy as np

from pycoingecko import CoinGeckoAPI
from sagemaker.predictor import Predictor
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer
from streamlit_autorefresh import st_autorefresh
import plotly.express as px

# ─── Config ─────────────────────────────────────────────────────────────────────
RAW_BUCKET   = os.environ.get('RAW_BUCKET', 'bitcoin-raw-prod-306104895673-us-east-1')
ENDPOINT     = "BitcoinPricePredictor"

# ─── Page Setup ─────────────────────────────────────────────────────────────────
st.set_page_config(page_title="BTC Dashboard", layout="wide")
st.title("📈 Real-Time BTC Price & Next-Minute Forecast")

# ─── Sidebar Controls ───────────────────────────────────────────────────────────
interval    = st.sidebar.slider("Refresh interval (seconds)", 10, 600, 60, step=10)
window_size = st.sidebar.slider("Forecast window size", 5, 100, 20, step=1)
if st.sidebar.button("Reset History"):
    st.session_state.clear()

# Refresh the app every `interval` seconds
st_autorefresh(interval=interval * 1000, key="refresh")

# ─── Initialize / Seed History ──────────────────────────────────────────────────
if "history" not in st.session_state:
    s3  = boto3.client("s3")
    obj = s3.get_object(Bucket=RAW_BUCKET, Key="bitcoin_prices.csv")
    df  = pd.read_csv(obj["Body"], parse_dates=["timestamp"])
    # keep only last 200 rows
    data = df.sort_values("timestamp").iloc[-200:]
    st.session_state.history = list(zip(data["timestamp"], data["price"]))
    st.session_state.forecast = []

# ─── Fetch Latest Price ─────────────────────────────────────────────────────────
cg    = CoinGeckoAPI()
now   = pd.Timestamp.now()
price = cg.get_price(ids="bitcoin", vs_currencies="usd")["bitcoin"]["usd"]

# Append & trim history
st.session_state.history.append((now, price))
st.session_state.history = st.session_state.history[-200:]

# ─── Make Next-Minute Prediction ────────────────────────────────────────────────
pred_price = None
pred_ts    = None

if len(st.session_state.history) >= window_size:
    # prepare LSTM input
    window = np.array([p for _, p in st.session_state.history[-window_size:]], float)
    payload = window.reshape(1, window_size, 1).tolist()

    predictor = Predictor(
        endpoint_name=ENDPOINT,
        serializer=JSONSerializer(),
        deserializer=JSONDeserializer()
    )
    resp = predictor.predict(payload)
    # resp is a delta
    delta = (resp["predictions"][0][0]
             if isinstance(resp, dict) and "predictions" in resp
             else resp[0][0])
    last_price        = st.session_state.history[-1][1]
    pred_price        = last_price + float(delta)
    pred_ts           = now + pd.Timedelta(minutes=1)

    st.session_state.forecast.append((pred_ts, pred_price))
    st.session_state.forecast = st.session_state.forecast[-100:]

# ─── Display Metrics ───────────────────────────────────────────────────────────
col1, col2 = st.columns(2)
col1.metric("Current BTC (USD)", f"${price:,.2f}")
if pred_price is not None:
    arrow = "▲" if pred_price > price else "▼"
    color = "green" if pred_price > price else "red"
    col2.markdown(
        f"**Next-Minute Forecast**  "
        f"<span style='color:{color};font-size:1.25em;'>{arrow}</span>  \n"
        f"**${pred_price:,.2f}**",
        unsafe_allow_html=True
    )
else:
    col2.write("Next-Minute Forecast: waiting…")

# ─── Plot Historical Prices (Hourly Ticks) ──────────────────────────────────────
hist_df = pd.DataFrame(
    {"timestamp":[t for t,_ in st.session_state.history],
     "price":     [p for _,p in st.session_state.history]}
)

fig_hist = px.line(
    hist_df, x="timestamp", y="price",
    title="Historical BTC Price",
    labels={"timestamp":"Time","price":"USD"}
)
fig_hist.update_layout(
    xaxis=dict(
        tickformat="%H:%M\n%b %d",
        dtick=3600*1000,  # one hour
    ),
    height=300
)
st.plotly_chart(fig_hist, use_container_width=True)

# ─── Plot Forecast Series (Hourly Ticks) ───────────────────────────────────────
if st.session_state.forecast:
    fc_df = pd.DataFrame(
        {"timestamp":[t for t,_ in st.session_state.forecast],
         "pred":      [p for _,p in st.session_state.forecast]}
    )

    fig_fc = px.line(
        fc_df, x="timestamp", y="pred",
        title="Next-Minute Forecast History",
        labels={"timestamp":"Time","pred":"USD"}
    )
    fig_fc.update_layout(
        xaxis=dict(
            tickformat="%H:%M\n%b %d",
            dtick=3600*1000,
        ),
        height=300
    )
    st.plotly_chart(fig_fc, use_container_width=True)
