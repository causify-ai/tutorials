import streamlit as st
from rasa_utils import BitcoinAPI
from requests.exceptions import HTTPError
import pandas as pd
import re
from datetime import datetime, timedelta

# --- Streamlit Setup ---
st.set_page_config(page_title="Bitcoin Chatbot", layout="centered")
st.title("💰 Bitcoin Chatbot")
st.markdown("Ask about Bitcoin price or basic Bitcoin facts.")

# --- Load Bitcoin API ---
@st.cache_resource
def load_api():
    return BitcoinAPI(vs_currency="usd")

api = load_api()

@st.cache_data(ttl=300)
def get_cached_price():
    return api.get_current_price()

@st.cache_data(ttl=300)
def get_cached_data(days, interval="daily"):
    return api.get_historical_data(days=days, interval=interval)

# --- User Input ---
user_input = st.text_input("Ask something about Bitcoin:", placeholder="e.g., What was the price 14 days ago?")

# --- Fixed Text Responses ---
FIXED_ANSWERS = {
    "what is bitcoin": "Bitcoin is a decentralized digital currency that allows peer-to-peer transactions without the need for a central authority.",
    "who created bitcoin": "Bitcoin was created by an unknown person or group under the pseudonym Satoshi Nakamoto in 2008.",
    "price of bitcoin tomorrow": "Sorry, I can't predict the future price of Bitcoin. Try checking market trends or analysis.",
}

# --- Response Logic ---
if user_input:
    txt = user_input.lower()

    try:
        # 1. General Info Questions
        if "what is bitcoin" in txt:
            st.info(FIXED_ANSWERS["what is bitcoin"])
        elif "who created bitcoin" in txt:
            st.info(FIXED_ANSWERS["who created bitcoin"])
        elif "price of bitcoin tomorrow" in txt:
            st.warning(FIXED_ANSWERS["price of bitcoin tomorrow"])

        # 2. Today's Price
        elif "price of bitcoin today" in txt or re.search(r"\bprice\b.*\btoday\b", txt):
            price = get_cached_price()
            st.success(f"Bitcoin price today is **${price:,.2f}**")

        # 3. Yesterday's Price
        elif "price of bitcoin yesterday" in txt or re.search(r"\bprice\b.*\byesterday\b", txt):
            df = get_cached_data(2)
            price = df.iloc[-2]["price"]
            day = df.iloc[-2]["timestamp"].strftime('%Y-%m-%d')
            st.success(f"Bitcoin price yesterday ({day}) was **${price:,.2f}**")

        # 4. 14-day history
        elif "price of bitcoin in 14 days" in txt or re.search(r"(14|fourteen)\s*[- ]?day", txt):
            df = get_cached_data(14)
            st.subheader("📊 Bitcoin Prices - Last 14 Days")
            st.line_chart(df.set_index("timestamp")["price"])

        # 5. 30-day history
        elif "price of bitcoin in 30 days" in txt or re.search(r"(30|thirty)\s*[- ]?day", txt):
            df = get_cached_data(30)
            stats = api.summarize_trends(df)
            st.subheader("📈 Bitcoin 30-Day Summary")
            st.write(f"**High**: ${stats['high']:,.2f}")
            st.write(f"**Low**: ${stats['low']:,.2f}")
            st.write(f"**Mean**: ${stats['mean']:,.2f}")
            st.line_chart(df.set_index("timestamp")["price"])

        else:
            st.warning("Sorry, I only answer Bitcoin-related questions like price today, yesterday, 14/30 days, or who/what Bitcoin is.")

    except HTTPError:
        st.error("⚠️ Rate limit hit. Please wait and try again shortly.")
    except Exception as e:
        st.error(f"⚠️ Something went wrong: {e}")
