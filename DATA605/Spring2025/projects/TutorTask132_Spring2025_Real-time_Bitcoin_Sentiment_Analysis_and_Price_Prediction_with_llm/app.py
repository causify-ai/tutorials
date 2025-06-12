import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import numpy as np
from keras.models import Sequential
from keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler
import os
from openai import OpenAI
from dotenv import load_dotenv


#Load environment variables
load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Streamlit Theme
st.set_page_config(page_title="Bitcoin Dashboard", layout="wide")
st.markdown("""
    <style>
        .main {
            background-color: #0b1e2d;
            color: #f5f5f5;
        }
        .stSidebar {
            background-color: #162737;
        }
        .css-1v0mbdj, .css-1n76uvr {
            color: #00f9ff;
        }
        .st-bw {
            background-color: #102030;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar Navigation
section = st.sidebar.radio("🌐 Navigate", ["Sentiment Overview", "Price & Predictions", "Forecast (LR + LSTM)", "Raw Data"])

# Load Data
sentiment_counts = pd.read_csv("sentiment_data/daily_sentiment_counts.csv")
sentiment_percent = pd.read_csv("sentiment_data/daily_sentiment_percent.csv")
price_data = pd.read_csv("merged_data/sentiment_price_data.csv")

# Convert Date
for df in [sentiment_counts, sentiment_percent, price_data]:
    df['date'] = pd.to_datetime(df['date'])

# Date Filter
date_range = st.sidebar.date_input("📅 Select date range:", [price_data['date'].min(), price_data['date'].max()])
mask = (price_data['date'] >= pd.to_datetime(date_range[0])) & (price_data['date'] <= pd.to_datetime(date_range[1]))
filtered_price = price_data[mask]
filtered_sentiment = sentiment_percent[(sentiment_percent['date'] >= pd.to_datetime(date_range[0])) & (sentiment_percent['date'] <= pd.to_datetime(date_range[1]))]

# Download Helper
def get_table_download_link(df, filename):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">📥 Download {filename}</a>'
    return href

# 1️⃣ Sentiment Overview
if section == "Sentiment Overview":
    st.title("📊 Real-time Bitcoin Sentiment Dashboard")
    st.header("📈 Daily Sentiment Distribution (%)")
    fig = px.area(
        filtered_sentiment,
        x="date",
        y=["Positive", "Neutral", "Negative"],
        title="Sentiment Breakdown Over Time",
        labels={"value": "Sentiment %", "date": "Date"},
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(get_table_download_link(filtered_sentiment, "filtered_sentiment_percent.csv"), unsafe_allow_html=True)

# 2️⃣ Price Trend
elif section == "Price & Predictions":
    st.title("💰 Bitcoin Price Trend")
    st.header("📉 Historical Bitcoin Price")
    fig2 = px.line(
        filtered_price,
        x="date",
        y="price",
        title="Bitcoin Price Over Time",
        labels={"price": "Price (USD)", "date": "Date"},
        template="plotly_dark",
        markers=True
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown(get_table_download_link(filtered_price, "filtered_price_data.csv"), unsafe_allow_html=True)

# 3️⃣ Forecasts
elif section == "Forecast (LR + LSTM)":
    st.title("📈 Forecasting Bitcoin Price with Sentiment")
    df = price_data.copy().dropna()

    # ---------- Linear Regression ----------
    st.subheader("🔷 Linear Regression Forecast")
    X = df[["Positive", "Neutral", "Negative"]]
    y = df["price"]
    lr_model = LinearRegression()
    lr_model.fit(X, y)
    df["lr_predicted"] = lr_model.predict(X)

    fig_lr = px.line(df, x="date", y=["price", "lr_predicted"],
                     labels={"value": "Price (USD)", "date": "Date"},
                     title="Actual vs Predicted Price (Linear Regression)",
                     template="plotly_dark")
    st.plotly_chart(fig_lr, use_container_width=True)
    st.success(f"📌 Linear Regression MSE: {mean_squared_error(y, df['lr_predicted']):.2f}")

    # ---------- LSTM Forecast ----------
    st.subheader("🟣 LSTM Forecast (Experimental)")
    # Only one feature used here for simplicity
    prices = df['price'].values.reshape(-1, 1)
    scaler = MinMaxScaler()
    scaled_prices = scaler.fit_transform(prices)

    sequence_length = 5
    X_lstm, y_lstm = [], []
    for i in range(sequence_length, len(scaled_prices)):
        X_lstm.append(scaled_prices[i-sequence_length:i, 0])
        y_lstm.append(scaled_prices[i, 0])

    X_lstm = np.array(X_lstm)
    y_lstm = np.array(y_lstm)
    X_lstm = np.reshape(X_lstm, (X_lstm.shape[0], X_lstm.shape[1], 1))

    model = Sequential()
    model.add(LSTM(50, return_sequences=False, input_shape=(X_lstm.shape[1], 1)))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X_lstm, y_lstm, epochs=10, batch_size=1, verbose=0)

    predicted_lstm = model.predict(X_lstm)
    predicted_lstm_rescaled = scaler.inverse_transform(predicted_lstm)
    lstm_actual = df["price"][sequence_length:].reset_index(drop=True)
    lstm_pred = pd.Series(predicted_lstm_rescaled.flatten())

    fig_lstm = px.line(x=lstm_actual.index, y=[lstm_actual, lstm_pred],
                       labels={"value": "Price (USD)", "index": "Days"},
                       title="LSTM Price Prediction vs Actual",
                       template="plotly_dark")
    fig_lstm.update_layout(legend=dict(title="Legend", itemsizing='constant'),
                           legend_title_text='Price Type')
    st.plotly_chart(fig_lstm, use_container_width=True)
    st.success(f"📌 LSTM MSE: {mean_squared_error(lstm_actual, lstm_pred):.2f}")

# 4️⃣ Raw Data View
elif section == "Raw Data":
    st.title("🧾 Data Viewer")
    st.header("📍 Latest Sentiment Counts")
    st.dataframe(sentiment_counts.tail(10), use_container_width=True)
    st.markdown(get_table_download_link(sentiment_counts, "sentiment_counts.csv"), unsafe_allow_html=True)

    st.header("📍 Merged Price + Sentiment Data")
    st.dataframe(price_data.tail(10), use_container_width=True)
    st.markdown(get_table_download_link(price_data, "sentiment_price_data.csv"), unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("🌐 Built using LLM, OpenAI, Prophet, LSTM, and Streamlit — Project605 2025")
