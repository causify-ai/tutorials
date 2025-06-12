import time
import requests
import pandas as pd
from ollama_API import generate_summary

def fetch_last_hour_prices() -> pd.DataFrame:
    now = int(time.time())
    one_hour_ago = now - 3600
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range"
    params = {"vs_currency": "usd", "from": one_hour_ago, "to": now}
    r = requests.get(url, params=params)
    r.raise_for_status()
    prices = r.json()["prices"]     # [[ms, price], …]

    df = pd.DataFrame(prices, columns=["timestamp_ms", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp_ms"], unit="ms")
    df = df.set_index("timestamp").drop(columns="timestamp_ms")

    # compute 15-min MA & volatility
    df["ma15"] = df["price"].rolling("15T", min_periods=1).mean()
    df["vol15"] = df["price"].rolling("15T", min_periods=2).std().fillna(0)
    return df

def summarize_bitcoin_last_hour() -> str:
    df = fetch_last_hour_prices()
    sample = df.iloc[::10]   # thin out for brevity

    lines = [
        f"{ts.strftime('%H:%M')}: price=${row.price:.2f}, "
        f"MA15=${row.ma15:.2f}, Vol15=${row.vol15:.2f}"
        for ts, row in sample.iterrows()
    ]

    prompt = (
        "Here are Bitcoin price metrics over the last hour (≈6-min intervals):\n"
        + "\n".join(lines)
        + "\n\nPlease summarize the short-term trend, highlighting moving average and volatility."
    )
    return generate_summary(prompt)

if __name__ == "__main__":
    print("Summary from Ollama:")
    print(summarize_bitcoin_last_hour())
