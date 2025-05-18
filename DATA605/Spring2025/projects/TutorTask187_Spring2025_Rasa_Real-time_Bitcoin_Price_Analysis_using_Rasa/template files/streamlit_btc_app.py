import streamlit as st
from rasa_utils import BitcoinAPI
import pandas as pd
import re

# Initialize the API once
api = BitcoinAPI(vs_currency="usd")

# Streamlit app
st.set_page_config(page_title="Bitcoin Chat", layout="centered")
st.title("💰 Bitcoin Chatbot")
st.markdown("Ask about Bitcoin price or recent trends (14 or 30 day windows).")

# User input
user_input = st.text_input("Ask something:", placeholder="e.g., What is the 30-day Bitcoin summary?")

# Respond based on input
if user_input:
    txt = user_input.lower()

    if re.search(r"\bprice\b", txt):
        price = api.get_current_price()
        st.success(f"The current Bitcoin price is **${price:,.2f}**.")

    elif re.search(r"(30|thirty)\s*[- ]?day", txt):
        df = api.get_historical_data(days=30, interval="daily")
        stats = api.summarize_trends(df)

        st.subheader("📈 30-Day Summary")
        st.write(f"**High**: ${stats['high']:,.2f}")
        st.write(f"**Low**: ${stats['low']:,.2f}")
        st.write(f"**Mean**: ${stats['mean']:,.2f}")
        st.line_chart(df.set_index("timestamp")["price"])

    elif re.search(r"(14|fourteen)\s*[- ]?day", txt):
        df = api.get_historical_data(days=14, interval="daily")

        st.subheader("📊 14-Day Price Chart")
        st.line_chart(df.set_index("timestamp")["price"])

    else:
        st.warning("Sorry, I only understand 'price', '30-day', or '14-day' queries.")

