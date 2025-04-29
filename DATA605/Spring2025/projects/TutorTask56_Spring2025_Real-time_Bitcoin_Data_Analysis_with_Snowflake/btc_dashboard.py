import streamlit as st
import pandas as pd
import snowflake.connector
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt

load_dotenv()

# -----------------------------
# 1. Snowflake connection setup
# -----------------------------
def load_data():
    conn = snowflake.connector.connect(
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA")
    )
    query = "SELECT * FROM bitcoin_prices ORDER BY timestamp"
    df = pd.read_sql(query, conn)
    conn.close()

    df.columns = df.columns.str.lower()  # Fix for uppercase column names
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    return df

# -----------------------
# 2. Streamlit Dashboard
# -----------------------
st.set_page_config(page_title="Bitcoin Dashboard", layout="wide")
st.title("📈 Real-Time Bitcoin Price Dashboard")

df = load_data()
st.success("✅ Data loaded from Snowflake!")

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
