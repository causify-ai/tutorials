import threading

import streamlit as st
from pipeline.schema_setup import setup_schema
from ingest.price_ingest import ingest_historical_prices, run_auto_ingest
from analysis.time_series_analysis import fetch_time_series_from_db
from analysis.time_series_analysis import compute_moving_average, detect_price_anomalies

# one‑time DB init + historical load
setup_schema()
try:
    ingest_historical_prices(days=365)
except Exception:
    st.warning("Historical ingest failed; proceeding…")

# start live ingestion in background
threading.Thread(
    target=run_auto_ingest, kwargs={"interval_sec": 60 * 60}, daemon=True
).start()


@st.cache_data(ttl=60)
def get_data():
    df = fetch_time_series_from_db()
    # df = compute_moving_average(df, window=10)
    # df = detect_price_anomalies(df, window=10, threshold=2.0)
    return df.set_index("timestamp")


def main():
    st.title("Bitcoin Price Dashboard (Streamlit)")

    df = get_data()

    # Main chart
    st.subheader("BTC Price (USD)")
    st.line_chart(df[["price"]])

    # Key stats
    st.markdown("### Key stats (last 365 days)")
    col1, col2, col3 = st.columns(3)
    col1.metric("Latest", f"${df['price'].iloc[-1]:,.2f}")
    col2.metric("Max", f"${df['price'].max():,.2f}")
    col3.metric("Min", f"${df['price'].min():,.2f}")


if __name__ == "__main__":
    main()
