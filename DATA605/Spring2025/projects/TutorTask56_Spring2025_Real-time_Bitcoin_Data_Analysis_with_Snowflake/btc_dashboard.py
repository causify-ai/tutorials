import streamlit as st
import pandas as pd
import snowflake.connector
import os
import matplotlib.pyplot as plt
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# 1. Snowflake connection setup
# -----------------------------
def load_data():
    # Load RSA private key
    key_path = os.getenv("SNOWFLAKE_PRIVATE_KEY")
    if not key_path or not os.path.exists(key_path):
        st.error(f"❌ RSA private key not found at path: {key_path}")
        st.stop()

    try:
        with open(key_path, "rb") as key_file:
            p_key = serialization.load_pem_private_key(key_file.read(), password=None)
            private_key_bytes = p_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
    except Exception as e:
        st.error(f"❌ Failed to load private key: {e}")
        st.stop()

    # Connect to Snowflake
    try:
        conn = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
            role=os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN"),
            private_key=private_key_bytes
        )
    except Exception as e:
        st.error(f"❌ Failed to connect to Snowflake: {e}")
        st.stop()

    # Query the data
    try:
        query = "SELECT * FROM bitcoin_prices ORDER BY timestamp"
        df = pd.read_sql(query, conn)
        conn.close()
    except Exception as e:
        st.error(f"❌ Failed to query Snowflake: {e}")
        st.stop()

    if df.empty:
        st.warning("⚠️ No data found in bitcoin_prices table.")
        st.stop()

    df.columns = df.columns.str.lower()

    if 'timestamp' not in df.columns or 'price' not in df.columns:
        st.error("❌ Table must have 'timestamp' and 'price' columns.")
        st.stop()

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    return df

# -----------------------
# 2. Streamlit Dashboard
# -----------------------
st.set_page_config(page_title="Bitcoin Dashboard", layout="wide")
st.title("📈 Real-Time Bitcoin Price Dashboard")

df = load_data()
st.success("✅ Data loaded successfully from Snowflake!")

# -----------------------
# 3. Key Metrics
# -----------------------
latest_price = df['price'].iloc[-1]
average_price = df['price'].mean()
volatility = df['price'].pct_change().std()

st.metric("💰 Latest Price", f"${latest_price:,.2f}")
st.metric("📊 Average Price", f"${average_price:,.2f}")
st.metric("⚡ Volatility (Std Dev %)", f"{volatility*100:.2f}%")

# -----------------------
# 4. Price Plot
# -----------------------
st.subheader("📉 BTC Price Over Time")
st.line_chart(df['price'])

# -----------------------
# 5. Moving Average Slider + Plot
# -----------------------
st.subheader("📏 Moving Average (MA)")
window = st.slider("Select MA Window (days):", 5, 30, 7)
df[f"ma_{window}"] = df['price'].rolling(window).mean()
st.line_chart(df[[f"ma_{window}", 'price']].dropna())

# -----------------------
# 6. Bollinger Bands
# -----------------------
st.subheader("📊 Bollinger Bands")

ma = df['price'].rolling(window=20).mean()
std = df['price'].rolling(window=20).std()
df['upper_band'] = ma + 2 * std
df['lower_band'] = ma - 2 * std

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(df.index, df['price'], label='BTC Price')
ax.plot(ma, label='20-Day MA', color='orange')
ax.plot(df['upper_band'], label='Upper Band', linestyle='--', color='green')
ax.plot(df['lower_band'], label='Lower Band', linestyle='--', color='red')
ax.fill_between(df.index, df['lower_band'], df['upper_band'], color='gray', alpha=0.2)
ax.set_title('Bitcoin Bollinger Bands')
ax.legend()
ax.grid()

st.pyplot(fig)
