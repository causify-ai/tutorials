import time
import pandas as pd
import requests

from ollama_API import generate_summary, generate_forecast
from prepare_finetune_data import fetch_prices

from dash import Dash, dcc, html, Input, Output
import plotly.graph_objs as go

# keep a module‐level cache of the last good DataFrame
_last_df = pd.DataFrame()

def fetch_and_process() -> pd.DataFrame:
    global _last_df

    now = int(time.time())
    one_hour_ago = now - 3600
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range"
    params = {"vs_currency": "usd", "from": one_hour_ago, "to": now}

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json().get("prices")
        if data is None:
            raise KeyError("missing ‘prices’ in response")
    except Exception as e:
        print(f"[ERROR] fetch_and_process: {e}")
        # fall back to last‐good data
        return _last_df.copy()

    df = pd.DataFrame(data, columns=["timestamp_ms", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp_ms"], unit="ms")
    df = df.set_index("timestamp").drop(columns="timestamp_ms")

    df["ma15"]  = df["price"].rolling("15T", min_periods=1).mean()
    df["vol15"] = df["price"].rolling("15T", min_periods=2).std().fillna(0)
    df["anomaly"] = (df["price"] - df["ma15"]).abs() > 2 * df["vol15"]

    _last_df = df.copy()
    return df

app = Dash(__name__)
app.layout = html.Div([
    html.H1("Real-Time Bitcoin Dashboard"),
    dcc.Graph(id="price-chart"),
    html.Button("Refresh", id="refresh-btn"),
    dcc.Interval(id="interval", interval=60*1000, n_intervals=0),
    html.Div(id="llm-summary",  style={"whiteSpace":"pre-wrap","marginTop":"1em"}),
    html.Div(id="llm-forecast", style={"whiteSpace":"pre-wrap","marginTop":"1em"}),
])

@app.callback(
    [ Output("price-chart",  "figure"),
      Output("llm-summary",  "children"),
      Output("llm-forecast", "children") ],
    [ Input("refresh-btn","n_clicks"),
      Input("interval",   "n_intervals") ]
)
def update(n_clicks, n_intervals):
    df = fetch_and_process()

    # build chart
    fig = go.Figure([
        go.Scatter(x=df.index, y=df["price"], name="Price"),
        go.Scatter(x=df.index, y=df["ma15"],  name="MA15"),
        go.Scatter(x=df[df.anomaly].index,
                   y=df[df.anomaly]["price"],
                   mode="markers",
                   marker=dict(color="red",size=8),
                   name="Anomaly")
    ])
    fig.update_layout(
        title="Bitcoin Price & 15-min MA (with anomalies)",
        xaxis_title="Time", yaxis_title="USD"
    )

    # summary
    sample = df.iloc[::10]
    lines = [
        f"{ts.strftime('%H:%M')}: ${row.price:.2f}, "
        f"MA15=${row.ma15:.2f}, Vol15=${row.vol15:.2f}"
        for ts,row in sample.iterrows()
    ]
    prompt = "Prices & metrics:\n" + "\n".join(lines) + "\n\nSummarize the trend."
    summary = generate_summary(prompt)

    # forecast (zero-shot)
    now    = int(time.time())
    series = fetch_prices(now - 12*300, now)
    vals   = series.tolist()
    prompt = (
        "Here are twelve 5-minute Bitcoin prices (USD):\n"
        + ", ".join(f"{v:.2f}" for v in vals)
        + "\n\nPlease predict the next 5-minute price."
    )
    forecast = generate_forecast(prompt)

    return fig, summary, f"Forecast (next 5 min): {forecast}"

if __name__=="__main__":
    app.run(host="0.0.0.0", port=8888)
