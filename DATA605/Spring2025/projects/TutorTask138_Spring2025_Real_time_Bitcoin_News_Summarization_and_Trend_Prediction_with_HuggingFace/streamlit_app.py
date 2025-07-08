import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from datetime import datetime

st.set_page_config(page_title="Bitcoin News Sentiment Dashboard", layout="wide")
st.title(" Bitcoin News Sentiment Dashboard")
st.caption("Real-time Bitcoin News Summarization and Trend Prediction")

# Load model
@st.cache_resource
def load_model():
    return joblib.load("xgb_model.pkl")

model = load_model()

# Load data
@st.cache_data
def load_data():
    sentiment = pd.read_csv("bitcoin_100_articles_summary.csv")
    forecast = pd.read_csv("btc_30_day_forecast.csv")
    return sentiment, forecast

df_sentiment, df_forecast = load_data()

# Section 1: Show latest summaries
st.subheader(" Latest Bitcoin News Summaries")
for _, row in df_sentiment.sort_values("published_date", ascending=False).head(5).iterrows():
    st.markdown(f"**{row['title']}**  \n{row['summary']}  \n*Sentiment: {row['sentiment']}*")
    st.write("---")

# Section 2: Sentiment over time
st.subheader(" Sentiment Over Time")
sentiment_avg = (
    df_sentiment.groupby("published_date")["sentiment"]
    .apply(lambda x: x.map({"POSITIVE": 1, "NEGATIVE": -1, "NEUTRAL": 0}).mean())
    .reset_index(name="sentiment_score")
)

plt.figure(figsize=(10, 4))
sns.lineplot(data=sentiment_avg, x="published_date", y="sentiment_score", marker="o", color="steelblue")
plt.xticks(rotation=45)
plt.title("Average Sentiment Score by Date")
plt.xlabel("Date")
plt.ylabel("Sentiment Score")
st.pyplot(plt.gcf())
plt.clf()

# Section 3: Forecast plot
st.subheader(" BTC Price Forecast for Next 30 Days")

plt.figure(figsize=(10, 4))
sns.lineplot(data=df_forecast, x="forecast_date", y="predicted_price", label="Predicted Price", linestyle="--", marker="o", color="royalblue")
plt.xticks(rotation=45)
plt.title("30-Day BTC Price Forecast")
plt.xlabel("Date")
plt.ylabel("Predicted Price (USD)")
st.pyplot(plt.gcf())
plt.clf()

# Section 4: Compare with actual prices if available
try:
    df_actual = pd.read_csv("actual_btc_prices_30.csv")
    df_actual["forecast_date"] = pd.to_datetime(df_actual["forecast_date"]).dt.date
    df_compare = pd.merge(df_forecast, df_actual, on="forecast_date")

    st.subheader("🔍 Actual vs. Predicted BTC Price (Last 30 Days)")

    plt.figure(figsize=(10, 4))
    plt.plot(df_compare["forecast_date"], df_compare["actual_price"], label="Actual Price", color="black", linewidth=2)
    plt.plot(df_compare["forecast_date"], df_compare["predicted_price"], label="Predicted Price", linestyle="--", color="royalblue", linewidth=2)
    plt.legend()
    plt.title("Actual vs. Predicted Bitcoin Price")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.xticks(rotation=45)
    st.pyplot(plt.gcf())
    plt.clf()

except FileNotFoundError:
    st.info(" No actual BTC prices available for comparison.")
# Section 5: Select a forecast date
st.subheader(" Select a Date to View Predicted BTC Price")

# Convert forecast_date column to datetime (if needed)
df_forecast["forecast_date"] = pd.to_datetime(df_forecast["forecast_date"])

# Let user select a date from available forecasts
available_dates = df_forecast["forecast_date"].dt.date.unique()
selected_date = st.selectbox("Select a forecast date:", sorted(available_dates))

# Display predicted price for that day
selected_row = df_forecast[df_forecast["forecast_date"].dt.date == selected_date]
if not selected_row.empty:
    predicted_price = selected_row.iloc[0]["predicted_price"]
    st.metric(label=f"Predicted BTC Price on {selected_date}", value=f"${predicted_price:,.2f}")
else:
    st.warning("No forecast available for this date.")
