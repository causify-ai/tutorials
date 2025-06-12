import time
import requests
import pandas as pd
from ollama_API import generate_summary
from prepare_finetune_data import fetch_prices
from dash import Dash, dcc, html, Input, Output
import plotly.graph_objs as go

def fetch_and_process() -> pd.DataFrame:
    """
    Fetch Bitcoin prices for the last hour and compute 15-min MA, volatility, and anomalies.
    """
    now = int(time.time())
    one_hour_ago = now - 3600
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range"
    params = {"vs_currency": "usd", "from": one_hour_ago, "to": now}
    data = requests.get(url, params=params).json()["prices"]

    df = pd.DataFrame(data, columns=["timestamp_ms", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp_ms"], unit="ms")
    df = df.set_index("timestamp").drop(columns="timestamp_ms")

    df["ma15"]  = df["price"].rolling("15T", min_periods=1).mean()
    df["vol15"] = df["price"].rolling("15T", min_periods=2).std().fillna(0)

    # anomaly when deviation > 2× rolling volatility
    df["anomaly"] = (df["price"] - df["ma15"]).abs() > 2 * df["vol15"]
    return df

app = Dash(__name__)
app.layout = html.Div([
    html.H1("Real-Time Bitcoin Dashboard"),
    dcc.Graph(id="price-chart"),
    html.Button("Refresh", id="refresh-btn"),
    dcc.Interval(id="interval", interval=60*1000, n_intervals=0),
    html.Div(id="llm-summary",  style={"whiteSpace": "pre-wrap", "marginTop": "1em"}),
    html.Div(id="llm-forecast",  style={"whiteSpace": "pre-wrap", "marginTop": "1em"}),
])

@app.callback(
    [
        Output("price-chart",    "figure"),
        Output("llm-summary",    "children"),
        Output("llm-forecast",   "children"),
    ],
    [
        Input("refresh-btn", "n_clicks"),
        Input("interval",    "n_intervals"),
    ]
)
def update(n_clicks, n_intervals):
    df = fetch_and_process()

    # build chart with price, MA15, and anomalies
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["price"], name="Price"))
    fig.add_trace(go.Scatter(x=df.index, y=df["ma15"],  name="MA15"))
    # anomalies as red markers
    fig.add_trace(go.Scatter(
        x=df[df.anomaly].index,
        y=df[df.anomaly]["price"],
        mode="markers",
        marker=dict(color="red", size=8),
        name="Anomaly"
    ))
    fig.update_layout(
        title="Bitcoin Price & 15-min MA (with anomalies)",
        xaxis_title="Time",
        yaxis_title="USD"
    )

    # LLM summary prompt
    sample = df.iloc[::10]
    lines = [
        f"{ts.strftime('%H:%M')}: ${row.price:.2f}, MA15=${row.ma15:.2f}, Vol15=${row.vol15:.2f}"
        for ts, row in sample.iterrows()
    ]
    prompt_summary = "Prices & metrics:\n" + "\n".join(lines) + "\n\nSummarize the trend."
    summary = generate_summary(prompt_summary)

    # zero-shot forecast prompt
    now    = int(time.time())
    series = fetch_prices(now - 12 * 300, now)
    vals   = series.tolist()
    prompt_f = (
        "Here are twelve 5-minute Bitcoin prices (USD):\n"
        + ", ".join(f"{v:.2f}" for v in vals)
        + "\n\nPlease predict the next 5-minute price."
    )
    forecast = generate_summary(prompt_f)

    return fig, summary, f"Forecast (next 5 min): {forecast}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888)
