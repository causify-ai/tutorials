import threading
import streamlit as st
import pandas as pd

from pipeline.schema_setup import setup_schema
from ingest.price_ingest import ingest_historical_prices, run_auto_ingest
from analysis.time_series_analysis import (
    fetch_time_series_from_db,
    compute_moving_averages,
    detect_price_anomalies,
    compute_bollinger_bands,
    compute_daily_returns,
    # forecast_with_arima,
    forecast_with_prophet,
)
import plotly.graph_objects as go

# from config.clickhouse_dashboards import register_default_btc_dashboard
import logging

logging.basicConfig(level=logging.INFO)

# Set wide layout as first Streamlit command
st.set_page_config(layout="wide")

# ───────────────────────────────────────────────
# INIT: Schema + Background ingestion
# ───────────────────────────────────────────────

setup_schema()

# register_default_btc_dashboard()

try:
    ingest_historical_prices(days=365)
except Exception as e:
    # st.warning("⚠️ Historical ingest failed; continuing with existing data…")
    logging.warning(f"⚠️ Historical ingest failed: {e} — continuing with existing data.")

threading.Thread(
    target=run_auto_ingest, kwargs={"interval_sec": 3600}, daemon=True
).start()

# ───────────────────────────────────────────────
# Caching DB Pull
# ───────────────────────────────────────────────


@st.cache_data(ttl=60)
def get_data():
    df = fetch_time_series_from_db()
    return df.set_index("timestamp")


# ───────────────────────────────────────────────
# Streamlit UI
# ───────────────────────────────────────────────


def main():
    st.title("📊 Real-Time Bitcoin Price Dashboard")
    st.success("✅ Data loaded successfully from ClickHouse!")

    df = get_data().reset_index()
    # ✅ Check if the DataFrame is empty
    if df.empty:
        st.error("❌ No data available. Please check ingestion or wait for retry.")
        return

    # Compute stats
    latest_price = df["price"].iloc[-1]
    avg_price = df["price"].mean()
    volatility = df["price"].pct_change().std() * 100

    # 1. Overview
    st.subheader("1. 📈 BTC Price Over Time")
    st.line_chart(df.set_index("timestamp")["price"])

    # 2. Key Stats
    st.subheader("2. 📊 Key Metrics (Last 365 Days)")
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Latest Price", f"${latest_price:,.2f}")
    col2.metric("📉 Average Price", f"${avg_price:,.2f}")
    col3.metric("⚡ Volatility (Std Dev %)", f"{volatility:.2f}%")

    # 3. Moving Averages
    st.subheader("3. 📏 Moving Average (MA)")
    ma_days = st.slider("Select MA Window (days):", min_value=3, max_value=60, value=7)
    df_ma = compute_moving_averages(df, days=[ma_days])
    st.line_chart(df_ma.set_index("timestamp")[["price", f"moving_average_{ma_days}d"]])

    # 4. Price Anomalies
    st.subheader("4. 🚨 Price Anomalies (±2σ)")
    df_anom = detect_price_anomalies(df, days=[ma_days], threshold=2.0)
    col = f"anomaly_{ma_days}d"
    with st.expander(f"{ma_days}-Day Anomalies"):
        st.scatter_chart(df_anom[df_anom[col]].set_index("timestamp")[["price"]])

    # 5. Bollinger Bands
    st.subheader("5. 📉 Bollinger Bands")
    bb_days = st.slider(
        "Select Bollinger Band Window (days):", min_value=5, max_value=60, value=20
    )
    df_bb = compute_bollinger_bands(df, days=bb_days)
    st.line_chart(df_bb.set_index("timestamp")[["price", "bb_upper", "bb_lower"]])

    # 6. Daily Returns
    st.subheader("6. 🔁 Daily Returns")
    df_ret = compute_daily_returns(df)
    st.line_chart(df_ret.set_index("timestamp")[["daily_return"]])
    # 7. Forecast with Prophet
    st.subheader("7. Forecasting with Prophet")
    try:
        forecast_df = forecast_with_prophet(df, periods=30)

        fig = go.Figure()

        # Plot historical BTC price
        fig.add_trace(
            go.Scatter(
                x=df["timestamp"],
                y=df["price"],
                name="Historical Price",
                line=dict(color="red"),
            )
        )

        # Plot forecast trend (yhat)
        fig.add_trace(
            go.Scatter(
                x=forecast_df["ds"],
                y=forecast_df["yhat"],
                name="Forecast Trend",
                line=dict(color="green"),
            )
        )

        # Plot upper confidence interval
        fig.add_trace(
            go.Scatter(
                x=forecast_df["ds"],
                y=forecast_df["yhat_upper"],
                name="Forecast Upper Bound",
                line=dict(color="orange"),
                mode="lines",
                showlegend=False,
            )
        )

        # Plot lower confidence interval with fill
        fig.add_trace(
            go.Scatter(
                x=forecast_df["ds"],
                y=forecast_df["yhat_lower"],
                name="Forecast Lower Bound",
                fill="tonexty",
                fillcolor="rgba(255,165,0,0.2)",
                line=dict(color="orange"),
                mode="lines",
                showlegend=False,
            )
        )

        fig.update_layout(
            title="Bitcoin Price Forecast (Prophet)",
            template="plotly_dark",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            legend_title="Legend",
        )

        st.plotly_chart(fig, use_container_width=True)

    except ValueError as e:
        print(f"❌ Skipping Prophet forecast: {e}")

    # 8. Forecast with ARIMA
    # st.subheader("8. 🧠 Forecasting with ARIMA")
    # try:
    #     df_daily = df.set_index("timestamp").resample("D").mean().dropna()
    #     forecast_arima = forecast_with_arima(df_daily, steps=30)
    #     future_index = pd.date_range(
    #         start=df_daily.index[-1] + pd.Timedelta(days=1), periods=30
    #     )
    #     arima_df = pd.DataFrame({"forecast": forecast_arima}, index=future_index)
    #     combined = pd.concat([df_daily["price"], arima_df["forecast"]], axis=1)
    #     st.line_chart(combined)
    # except Exception as e:
    #     st.error(f"ARIMA forecast failed: {e}")


if __name__ == "__main__":
    main()
