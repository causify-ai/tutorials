import pandas as pd
import numpy as np
import altair as alt
import yfinance as yf
from datetime import datetime, timedelta
import requests

def apply_transforms(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['rsi'] = df['close'].rolling(window=14).apply(lambda x: 100 - (100 / (1 + x.pct_change().mean())))
    df['bollinger_upper'] = df['close'].rolling(window=20).mean() + 2 * df['close'].rolling(window=20).std()
    df['bollinger_lower'] = df['close'].rolling(window=20).mean() - 2 * df['close'].rolling(window=20).std()
    df['volatility'] = df['close'].rolling(window=10).std()
    df['volume_ma'] = df['volume'].rolling(window=5).mean()
    df.columns = [str(c) for c in df.columns]
    return df

def compute_volatility_surface(df: pd.DataFrame):
    surfaces = []
    for window in [5, 10, 15, 30, 60]:
        temp = df.copy()
        temp['volatility'] = temp['close'].rolling(window=window).std()
        temp['window'] = window
        surfaces.append(temp[['timestamp', 'window', 'volatility']])
    return pd.concat(surfaces)

def simulate_mempool_data(df: pd.DataFrame):
    mempool = df[['timestamp']].copy()
    mempool['tx_size'] = np.random.exponential(scale=250, size=len(mempool))
    return mempool

def generate_dashboard(df: pd.DataFrame):
    selection = alt.selection_interval(encodings=['x'])
    base = alt.Chart(df).encode(x=alt.X('timestamp:T', title='Time', axis=alt.Axis(labelAngle=-45))).properties(width=800)
    price = base.mark_line(strokeWidth=2, color='steelblue').encode(y=alt.Y('close:Q', title='Price (USD)'))
    bollinger_band = base.mark_area(opacity=0.2, color='lightblue').encode(y='bollinger_lower:Q', y2='bollinger_upper:Q')
    price_layer = alt.layer(price, bollinger_band).add_selection(selection).properties(title=' BTC Price with Bollinger Bands')
    volume = base.mark_bar(opacity=0.4, color='gray').encode(y=alt.Y('volume:Q', title='Volume (USD)')).properties(title=' Trading Volume').transform_filter(selection)
    rsi = base.mark_line(strokeWidth=2, color='orange').encode(y=alt.Y('rsi:Q', title='RSI')).properties(title=' Relative Strength Index (RSI)').transform_filter(selection)
    vol_df = compute_volatility_surface(df)
    heatmap = alt.Chart(vol_df).mark_rect().encode(x=alt.X('timestamp:T'), y=alt.Y('window:O'), color=alt.Color('volatility:Q', scale=alt.Scale(scheme='blues'))).properties(title=' Volatility Surface', width=800).transform_filter(selection)
    mempool_df = simulate_mempool_data(df)
    mempool_hist = alt.Chart(mempool_df).mark_bar(opacity=0.7, color='seagreen').encode(x=alt.X('tx_size:Q', bin=alt.Bin(maxbins=30)), y=alt.Y('count()')).properties(title=' Mempool Transaction Size Distribution', width=800)
    return alt.vconcat(price_layer, volume, rsi, heatmap, mempool_hist).configure_axis(labelFontSize=12, titleFontSize=14).configure_view(stroke=None).configure_title(fontSize=16, anchor='start')

def fetch_binance_latest_candle():
    url = "https://api.binance.com/api/v3/klines"
    params = { "symbol": "BTCUSDT", "interval": "15m", "limit": 1 }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        kline = response.json()[0]
        return {
            "timestamp": pd.to_datetime(kline[0], unit="ms"),
            "open": float(kline[1]),
            "high": float(kline[2]),
            "low": float(kline[3]),
            "close": float(kline[4]),
            "volume": float(kline[5])
        }
    return None

def get_combined_data():
    end = datetime.utcnow()
    start = end - timedelta(days=7)
    df = yf.download("BTC-USD", interval="15m", start=start, end=end)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.columns = [str(c).strip() for c in df.columns]
    df = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
    df = df.reset_index()
    df["timestamp"] = pd.to_datetime(df["Datetime"])
    df = df[["timestamp", "open", "high", "low", "close", "volume"]]
    latest = fetch_binance_latest_candle()
    if latest:
        df = pd.concat([df, pd.DataFrame([latest])], ignore_index=True)
    return df