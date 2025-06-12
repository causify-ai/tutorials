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
        df = df.dropna(subset=['timestamp'])  # Remove invalid timestamps

        # Ensure both columns exist
        if "note" not in df.columns:
            df["note"] = ""
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(columns=["timestamp", "predicted_price", "note"])

df = load_data()

if df.empty:
    st.warning("Waiting for predictions to be logged...")
else:
    try:
        # Filter valid price predictions only
        pred_df = df.dropna(subset=["predicted_price"])

        # Format for display
        pred_df["formatted_time"] = pred_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
        pred_df = pred_df.set_index("formatted_time")

        # Line chart
        st.line_chart(pred_df["predicted_price"])

        # Table view with annotations
        display_df = df.sort_values("timestamp", ascending=False).tail(10)
        st.subheader("📋 Recent Predictions")
        st.dataframe(display_df[["timestamp", "predicted_price", "note"]], use_container_width=True)
    except Exception as e:
        st.error(f"Error rendering dashboard: {e}")

st.caption("Updates every 60 seconds. Make sure the scheduler is running and btc_predictions_log.csv is available.")
