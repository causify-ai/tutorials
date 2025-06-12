
import pandas as pd
import numpy as np
import altair as alt
import requests
from datetime import datetime, timedelta

_last_df = None
_last_fetch_time = None

def fetch_kraken_data():
    url = "https://api.kraken.com/0/public/OHLC"
    since = int((datetime.utcnow() - timedelta(days=7)).timestamp())
    params = {
        "pair": "XBTUSD",
        "interval": 15,
        "since": since
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "error" in data and data["error"]:
        raise ValueError("Kraken API error: " + str(data["error"]))

    result_key = next(iter(data["result"]))
    ohlc_data = data["result"][result_key]

    df = pd.DataFrame(ohlc_data, columns=[
        "timestamp", "open", "high", "low", "close", "vwap", "volume", "count"
    ])

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)

    return df[["timestamp", "open", "high", "low", "close", "volume"]]

def get_combined_data():
    global _last_df, _last_fetch_time

    if _last_df is not None and _last_fetch_time and (datetime.utcnow() - _last_fetch_time).seconds < 300:
        print("Using cached Kraken data.")
        return _last_df

    try:
        df = fetch_kraken_data()
        _last_df = df
        _last_fetch_time = datetime.utcnow()
        return df

    except Exception as e:
        print(f"Kraken fetch failed: {e}")
        print("Loading fallback CSV...")
        try:
            df = pd.read_csv("fallback_btc.csv")
            if "timestamp" not in df.columns:
                raise ValueError("Missing 'timestamp' column in fallback CSV.")
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df.columns = [str(c).strip().lower() for c in df.columns]
            df = df[["timestamp", "open", "high", "low", "close", "volume"]]
            return df
        except Exception as e:
            raise RuntimeError("Failed to load fallback CSV: " + str(e))

def apply_transforms(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["rsi"] = df["close"].rolling(window=14).apply(lambda x: 100 - (100 / (1 + x.pct_change().mean())))
    df["bollinger_upper"] = df["close"].rolling(window=20).mean() + 2 * df["close"].rolling(window=20).std()
    df["bollinger_lower"] = df["close"].rolling(window=20).mean() - 2 * df["close"].rolling(window=20).std()
    df["volatility"] = df["close"].rolling(window=10).std()
    df["volume_ma"] = df["volume"].rolling(window=5).mean()
    df.columns = [str(c) for c in df.columns]
    return df

def compute_volatility_surface(df: pd.DataFrame):
    surfaces = []
    for window in [5, 10, 15, 30, 60]:
        temp = df.copy()
        temp["volatility"] = temp["close"].rolling(window=window).std()
        temp["window"] = window
        surfaces.append(temp[["timestamp", "window", "volatility"]])
    return pd.concat(surfaces)

def simulate_mempool_data(df: pd.DataFrame):
    mempool = df[["timestamp"]].copy()
    mempool["tx_size"] = np.random.exponential(scale=250, size=len(mempool))
    return mempool

def generate_dashboard(df: pd.DataFrame):
    selection = alt.selection_interval(encodings=["x"])
    base = alt.Chart(df).encode(x=alt.X("timestamp:T", title="Time", axis=alt.Axis(labelAngle=-45))).properties(width=800)

    price = base.mark_line(strokeWidth=2).encode(y=alt.Y("close:Q", title="Price (USD)"))
    bollinger_band = base.mark_area(opacity=0.2).encode(y="bollinger_lower:Q", y2="bollinger_upper:Q")
    price_layer = alt.layer(price, bollinger_band).add_selection(selection).properties(title="BTC Price with Bollinger Bands")

    volume = base.mark_bar(opacity=0.4).encode(y=alt.Y("volume:Q", title="Volume (USD)")).properties(title="Trading Volume").transform_filter(selection)
    rsi = base.mark_line(strokeWidth=2).encode(y=alt.Y("rsi:Q", title="RSI")).properties(title="Relative Strength Index (RSI)").transform_filter(selection)

    vol_df = compute_volatility_surface(df)
    heatmap = alt.Chart(vol_df).mark_rect().encode(
        x=alt.X("timestamp:T"),
        y=alt.Y("window:O"),
        color=alt.Color("volatility:Q", scale=alt.Scale(scheme="blues"))
    ).properties(title="Volatility Surface", width=800).transform_filter(selection)

    mempool_df = simulate_mempool_data(df)
    mempool_hist = alt.Chart(mempool_df).mark_bar(opacity=0.7).encode(
        x=alt.X("tx_size:Q", bin=alt.Bin(maxbins=30)),
        y=alt.Y("count()")
    ).properties(title="Mempool Transaction Size Distribution", width=800)

    return alt.vconcat(price_layer, volume, rsi, heatmap, mempool_hist).configure_axis(labelFontSize=12, titleFontSize=14).configure_view(stroke=None).configure_title(fontSize=16, anchor="start")
