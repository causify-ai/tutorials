from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import httpx
import pandas as pd
import plotly.graph_objects as go
from plotly.io import to_html

app = FastAPI()


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    # Fetch real-time Bitcoin price
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": "bitcoin", "vs_currencies": "usd"}
        response = httpx.get(url, params=params)
        live_price = response.json()["bitcoin"]["usd"]
    except Exception:
        live_price = "Unavailable"

    # Load historical price data
    df = pd.read_csv("bitcoin_5yr_history.csv")
    df["moving_avg"] = df["price"].rolling(window=30).mean()
    df["std_dev"] = df["price"].rolling(window=30).std()
    df["upper_band"] = df["moving_avg"] + 2 * df["std_dev"]
    df["lower_band"] = df["moving_avg"] - 2 * df["std_dev"]
    df["anomaly"] = (df["price"] > df["upper_band"]) | (df["price"] < df["lower_band"])

    # Chart 1: Price + Moving Average
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=df["date"], y=df["price"], name="Price", mode="lines", line=dict(color='deepskyblue')))
    fig1.add_trace(go.Scatter(x=df["date"], y=df["moving_avg"], name="Moving Avg", mode="lines", line=dict(color='gold', dash='dash')))
    fig1.update_layout(title="📈 Bitcoin Price + 30-Day Moving Average", template="plotly_dark", xaxis_title="Date", yaxis_title="USD")

    # Chart 2: Moving Average only
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df["date"], y=df["moving_avg"], name="30-Day Moving Avg", mode="lines", line=dict(color='orange')))
    fig2.update_layout(title="📉 30-Day Moving Average (Standalone)", template="plotly_dark", xaxis_title="Date", yaxis_title="USD")

    # Chart 3: Anomalies
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=df["date"], y=df["price"], name="Price", mode="lines", line=dict(color='lightblue')))
    fig3.add_trace(go.Scatter(x=df["date"][df["anomaly"]], y=df["price"][df["anomaly"]], mode="markers",
                              name="Anomalies", marker=dict(color='red', size=8)))
    fig3.update_layout(title="🚨 Anomalies in Bitcoin Price (Bollinger-based)", template="plotly_dark", xaxis_title="Date", yaxis_title="USD")

    # Combine all into one HTML response
    html = f"""
    <html>
        <head>
            <meta charset='utf-8'>
            <title>Bitcoin Dashboard</title>
        </head>
        <body style='background-color:#111; color:white; font-family:sans-serif;'>
            <h1 style='text-align:center;'>🪙 Real-Time Bitcoin Price: <span style='color:gold;'>${live_price}</span></h1>
            {to_html(fig1, include_plotlyjs='cdn', full_html=False)}
            <hr>
            <h2 style='text-align:center;'>📉 30-Day Moving Average (Standalone)</h2>
            {to_html(fig2, include_plotlyjs=False, full_html=False)}
            <hr>
            <h2 style='text-align:center;'>🚨 Bollinger Band Anomalies</h2>
            {to_html(fig3, include_plotlyjs=False, full_html=False)}
        </body>
    </html>
    """.strip()

    return HTMLResponse(content=html)