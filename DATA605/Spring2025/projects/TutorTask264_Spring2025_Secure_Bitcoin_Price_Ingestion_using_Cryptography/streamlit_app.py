import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from SecureBitcoin_utils import *
from datetime import datetime, timezone
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf
import io

# Configure page
st.set_page_config(page_title="Secure BTC Analyzer", layout="wide")

st.title("🔐 Secure Bitcoin Price Analyzer")
st.markdown("This app fetches encrypted Bitcoin price data, decrypts it, and analyzes trends over 15 days (hourly resolution).")

# Derive key
key = derive_key("strong_secure_password")



# --- Section: Historical Encrypted Analysis ---
@st.cache_data(ttl=300, show_spinner=True)



def load_historical_data():
    data = fetch_hourly_data(days=15)
    encrypted = [encrypt_data(d, key) for d in data]
    decrypted = [decrypt_data(e, key) for e in encrypted]
    df = pd.DataFrame(decrypted)
    df['timestamp'] = pd.to_datetime(df['timestamp'], format="ISO8601")
    df['price_usd'] = df['price_usd'].astype(float)
    df = df.sort_values("timestamp").set_index("timestamp")
    return df

# --- Button to Fetch Real-Time Price ---
st.subheader("⏱️ Get Real-Time BTC Price")

if st.button("📥 Fetch Real-Time Price"):
    realtime = fetch_bitcoin_price()
    st.success(f"Current BTC Price: **${realtime['price_usd']}** (as of {realtime['timestamp']})")

if st.button("Refresh Data Now"):
    load_historical_data.clear()
    st.toast("Cache cleared! Please refresh the page to reload data.")

df = load_historical_data()

import matplotlib.dates as mdates


st.subheader("📈 Bitcoin Price (15-Day Hourly)")

fig1, ax1 = plt.subplots(figsize=(12, 4))
ax1.plot(df.index, df['price_usd'], marker='o', markersize=2)
ax1.set_title("Bitcoin Price (Last 15 Days)")
ax1.set_ylabel("Price (USD)")
ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1))
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
ax1.grid(True)
fig1.autofmt_xdate()
st.pyplot(fig1)


# --- Moving Averages ---
# Calculate moving averages
df['SMA_6'] = df['price_usd'].rolling(window=6).mean()
df['EMA_6'] = df['price_usd'].ewm(span=6).mean()

import plotly.graph_objects as go

st.subheader("📊 BTC Chart with SMA & EMA")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df.index,
    y=df['price_usd'],
    mode='lines',
    name='Price',
    line=dict(color='royalblue'),
    hovertemplate='Time: %{x}<br>Price: $%{y:.2f}'
))

fig.add_trace(go.Scatter(
    x=df.index,
    y=df['SMA_6'],
    mode='lines',
    name='SMA 6',
    line=dict(dash='dot', color='orange'),
    hovertemplate='Time: %{x}<br>SMA: $%{y:.2f}'
))

fig.add_trace(go.Scatter(
    x=df.index,
    y=df['EMA_6'],
    mode='lines',
    name='EMA 6',
    line=dict(dash='dot', color='green'),
    hovertemplate='Time: %{x}<br>EMA: $%{y:.2f}'
))

fig.update_layout(
    title="Bitcoin Price + SMA/EMA",
    xaxis_title="Time",
    yaxis_title="Price (USD)",
    hovermode="x unified",
    template="plotly_dark"
)

st.plotly_chart(fig, use_container_width=True)




# --- Decomposition ---
st.subheader("📉 Trend Decomposition")

result = seasonal_decompose(df['price_usd'], model='additive', period=24)

fig, axes = plt.subplots(4, 1, figsize=(12, 8), sharex=True)

result.observed.plot(ax=axes[0], title="Observed")
axes[0].grid(True)

result.trend.plot(ax=axes[1], title="Trend")
axes[1].grid(True)

result.seasonal.plot(ax=axes[2], title="Seasonality")
axes[2].grid(True)

result.resid.plot(ax=axes[3], title="Residuals")
axes[3].grid(True)

fig.tight_layout(h_pad=2)  # Add padding between subplots
fig.autofmt_xdate()       # Auto-rotate x-axis labels
st.pyplot(fig)


# --- ACF Plot ---
st.subheader("🔁 Autocorrelation (ACF)")
acf_fig, acf_ax = plt.subplots()
plot_acf(df['price_usd'], lags=50, ax=acf_ax)
st.pyplot(acf_fig)

st.subheader("💾 Download Decrypted Data")

csv_data = df.reset_index().to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download CSV",
    data=csv_data,
    file_name="decrypted_bitcoin_data.csv",
    mime="text/csv"
)

from statsmodels.tsa.holtwinters import ExponentialSmoothing

st.subheader("🔮 Bitcoin Forecasting: Holt-Winters (24h)")

# Model and forecast next 24 hours
model = ExponentialSmoothing(df['price_usd'], trend='add', seasonal='add', seasonal_periods=24)
hw_fit = model.fit()
forecast = hw_fit.forecast(24)



import plotly.graph_objects as go

from datetime import timedelta

# Forecast next 24 hours
model = ExponentialSmoothing(df['price_usd'], trend='add', seasonal='add', seasonal_periods=24)
hw_fit = model.fit()
forecast = hw_fit.forecast(24)

# Fix forecast index to be datetime
future_index = pd.date_range(start=df.index[-1] + timedelta(hours=1), periods=24, freq='H')
forecast.index = future_index

import plotly.graph_objects as go
from datetime import timedelta

# (Assuming `df` and `forecast` are already defined as before)

# Fix forecast index
future_index = pd.date_range(start=df.index[-1] + timedelta(hours=1),
                             periods=len(forecast), freq='H')
forecast.index = future_index

fig = go.Figure()

# Actual line (no markers)
fig.add_trace(go.Scatter(
    x=df.index,
    y=df['price_usd'],
    mode='lines',
    name='Actual',
    line=dict(color='royalblue', width=2),
    hovertemplate='Time: %{x|%b %d %H:%M}<br>Price: $%{y:.2f}<extra></extra>'
))

# Forecast line (dashed)
fig.add_trace(go.Scatter(
    x=forecast.index,
    y=forecast,
    mode='lines',
    name='Forecast',
    line=dict(color='orange', width=2, dash='dash'),
    hovertemplate='Time: %{x|%b %d %H:%M}<br>Forecast: $%{y:.2f}<extra></extra>'
))

fig.update_layout(
    title="Holt-Winters BTC Forecast (Next 24 Hours)",
    xaxis_title="Time",
    yaxis_title="Price (USD)",
    hovermode="x unified",
    template="plotly_dark",
    xaxis=dict(
        tickformat="%b %d",
        rangeslider=dict(visible=True),
        type="date"
    ),
    margin=dict(l=40, r=20, t=60, b=40)
)

st.plotly_chart(fig, use_container_width=True)

from sklearn.ensemble import IsolationForest
import numpy as np

st.subheader("🚨 Anomaly Detection")

# 1) Z-scores & Bollinger Bands
window = 24  # 24-hour window
df['rolling_mean'] = df['price_usd'].rolling(window).mean()
df['rolling_std']  = df['price_usd'].rolling(window).std()
df['z_score']     = (df['price_usd'] - df['rolling_mean']) / df['rolling_std']
df['bb_upper']    = df['rolling_mean'] + 2 * df['rolling_std']
df['bb_lower']    = df['rolling_mean'] - 2 * df['rolling_std']

# mark Bollinger anomalies
df['bb_anomaly'] = ((df['price_usd'] > df['bb_upper']) |
                   (df['price_usd'] < df['bb_lower']))

# 2) MACD
ema_short = df['price_usd'].ewm(span=12).mean()
ema_long  = df['price_usd'].ewm(span=26).mean()
df['macd']    = ema_short - ema_long
df['macd_sig']= df['macd'].ewm(span=9).mean()
df['macd_anomaly'] = ((df['macd'] > df['macd_sig']) & 
                     (df['macd'].shift() <= df['macd_sig'].shift()))

# 3) Isolation Forest
isf = IsolationForest(contamination=0.01, random_state=42)
# reshape into 2D array for sklearn
scores = isf.fit_predict(df[['price_usd']])
df['iforest_anomaly'] = scores == -1

# Show summary table
anoms = df.loc[df[['bb_anomaly','macd_anomaly','iforest_anomaly']].any(axis=1),
               ['price_usd','z_score','bb_upper','bb_lower','macd','macd_sig',
                'bb_anomaly','macd_anomaly','iforest_anomaly']]
st.markdown("#### Detected anomalies")
st.dataframe(anoms)

# Plot anomalies on the main price chart
import plotly.graph_objects as go

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df.index, y=df['price_usd'],
    mode='lines', name='Price',
    line=dict(color='royalblue', width=2)
))

# highlight BB anomalies
bb_pts = df[df['bb_anomaly']]
fig.add_trace(go.Scatter(
    x=bb_pts.index, y=bb_pts['price_usd'],
    mode='markers', name='BB Outlier',
    marker=dict(color='red', size=6),
    hovertemplate='Time:%{x}<br>Price:%{y:.2f}<extra></extra>'
))

# highlight MACD anomalies
macd_pts = df[df['macd_anomaly']]
fig.add_trace(go.Scatter(
    x=macd_pts.index, y=macd_pts['price_usd'],
    mode='markers', name='MACD Signal',
    marker=dict(color='orange', size=6),
    hovertemplate='Time:%{x}<br>Price:%{y:.2f}<extra></extra>'
))

# highlight Isolation Forest anomalies
if_pts = df[df['iforest_anomaly']]
fig.add_trace(go.Scatter(
    x=if_pts.index, y=if_pts['price_usd'],
    mode='markers', name='IForest Anomaly',
    marker=dict(color='magenta', size=6),
    hovertemplate='Time:%{x}<br>Price:%{y:.2f}<extra></extra>'
))

fig.update_layout(
    title="Price with Anomaly Highlights",
    xaxis_title="Time",
    yaxis_title="USD",
    hovermode="x unified",
    template="plotly_dark",
    xaxis=dict(tickformat="%b %d %H:%M", rangeslider=dict(visible=True))
)
st.plotly_chart(fig, use_container_width=True)



