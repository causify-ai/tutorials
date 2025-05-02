# btc_forecast_app.py

import streamlit as st
import pandas as pd
import numpy as np
import torch
import joblib
import yfinance as yf
import matplotlib.pyplot as plt

from torch import nn
from datetime import datetime

# --- Model Class ---
class TimeSeriesTransformer(nn.Module):
    def __init__(self, input_dim=1, d_model=64, nhead=4, num_layers=2, dropout=0.1):
        super(TimeSeriesTransformer, self).__init__()
        self.input_projection = nn.Linear(input_dim, d_model)
        self.positional_encoding = nn.Parameter(torch.randn(5000, d_model))
        encoder_layer = nn.TransformerEncoderLayer(d_model=d_model, nhead=nhead, dropout=dropout)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.output_layer = nn.Linear(d_model, 1)

    def forward(self, src):
        batch_size, seq_len, _ = src.shape
        src = self.input_projection(src)
        pe = self.positional_encoding[:seq_len, :].unsqueeze(0).repeat(batch_size, 1, 1)
        src = src + pe
        src = src.permute(1, 0, 2)
        transformer_output = self.transformer_encoder(src)
        out = transformer_output[-1, :, :]
        return self.output_layer(out)

# --- Prediction Function ---
def predict_future_prices(model, last_sequence, n_days, scaler, device):
    model.eval()
    preds = []
    seq = last_sequence.copy()
    for _ in range(n_days):
        input_tensor = torch.tensor(seq.reshape(1, -1, 1), dtype=torch.float32).to(device)
        with torch.no_grad():
            pred = model(input_tensor).cpu().numpy()[0][0]
        preds.append(pred)
        seq = np.append(seq[1:], pred)
    return scaler.inverse_transform(np.array(preds).reshape(-1, 1))

# --- Load Model & Scaler ---
@st.cache_resource
def load_model_and_scaler():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = TimeSeriesTransformer().to(device)
    model.load_state_dict(torch.load("transformer_btc_model.pth", map_location=device))
    model.eval()
    scaler = joblib.load("btc_scaler.save")
    return model, scaler, device

# --- Fetch BTC Data ---
@st.cache_data
def load_btc_data():
    df = yf.download("BTC-USD", start="2013-04-28", interval='1d')
    df = df[['Close']].rename(columns={'Close': 'price'})
    df.reset_index(inplace=True)
    df['timestamp'] = pd.to_datetime(df['Date'])
    df = df[['timestamp', 'price']].dropna()
    return df

# --- Streamlit UI ---
st.title("🔮 Bitcoin Price Forecasting")
st.markdown("This app predicts future Bitcoin prices using a Transformer model.")

n_days = st.slider("Select days to forecast", min_value=1, max_value=30, value=7)

# Load data
btc_hist = load_btc_data()
model, scaler, device = load_model_and_scaler()

# Normalize
btc_hist['scaled_price'] = scaler.transform(btc_hist[['price']])
sequence_length = 30
last_seq = btc_hist['scaled_price'].values[-sequence_length:]

# Predict
preds = predict_future_prices(model, last_seq, n_days, scaler, device)

# Combine with historical
past_prices = btc_hist.tail(sequence_length).copy()
past_prices['label'] = "Past Price"

future_dates = pd.date_range(start=past_prices['timestamp'].iloc[-1] + pd.Timedelta(days=1), periods=n_days)
future_df = pd.DataFrame({'timestamp': future_dates, 'price': preds.flatten(), 'label': 'Forecasted Price'})

plot_df = pd.concat([past_prices[['timestamp', 'price', 'label']], future_df])

# Plot
st.subheader("Bitcoin Price Forecast")
fig, ax = plt.subplots(figsize=(10, 5))
for label, group in plot_df.groupby("label"):
    ax.plot(group['timestamp'], group['price'], label=label, marker='o' if label=="Forecasted Price" else None)
ax.set_xlabel("Date")
ax.set_ylabel("BTC Price (USD)")
ax.legend()
ax.grid(True)
st.pyplot(fig)