import streamlit as st
import pandas as pd

st.set_page_config(page_title="BTC Price Predictor Dashboard", layout="centered")
st.title("📈 Real-Time Bitcoin Price Prediction Dashboard")

log_file = "btc_predictions_log.csv"

@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(log_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.dropna(subset=['timestamp'])  # remove rows with invalid timestamps
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(columns=["timestamp", "predicted_price"])

df = load_data()

if df.empty:
    st.warning("Waiting for predictions to be logged...")
else:
    try:
        # Format timestamp for better X-axis readability
        df["formatted_time"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
        df_display = df.set_index("formatted_time")

        # Display line chart
        st.line_chart(df_display["predicted_price"])

        # Display last 10 predictions in a table
        st.dataframe(df.sort_values("timestamp", ascending=False).tail(10), use_container_width=True)
    except Exception as e:
        st.error(f"Error rendering dashboard: {e}")

st.caption("Updates every 60 seconds. Make sure the scheduler is running.")
