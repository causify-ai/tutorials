from dash import Dash, html, dcc, Output, Input
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.analyze_traces import (
    load_trace_data,
    compute_hourly_metrics,
    compute_daily_metrics,
    forecast_hourly_latency,
    forecast_daily_latency
)
from visualization.forecast_visualizer import (
    visualize_forecast,
    plot_anomaly,
    plot_price_over_time
)

# Initialize Dash app
app = Dash(__name__)
app.title = "Latency Prediction Dashboard"

# Layout with refresh interval
app.layout = html.Div([
    html.H1("📊 Real-Time Latency Forecast Dashboard", style={"textAlign": "center"}),

    dcc.Interval(id="refresh", interval=60*60*1000, n_intervals=0),

    html.Div([
        html.H3("Bitcoin Price Over Time", style={"marginTop": 40}),
        dcc.Graph(id="btc-price")
    ]),

    html.Div([
        html.H3("Predicted Latency vs Actual (Hourly)", style={"marginTop": 40}),
        dcc.Graph(id="latency-forecast-hourly")
    ]),

    html.Div([
        html.H3("Predicted Latency vs Actual (Daily)", style={"marginTop": 40}),
        dcc.Graph(id="latency-forecast-daily")
    ]),

    html.Div([
    html.H3("Latency Anomaly Detection", style={"marginTop": 40}),
    dcc.Graph(id="latency-anomalies")
    ])
])

# CALLBACKS FOR LIVE UPDATES
@app.callback(
    Output("latency-forecast-hourly", "figure"),
    Input("refresh", "n_intervals")
)
def update_hourly_forecast(_):
    df = load_trace_data()
    hourly_df = forecast_hourly_latency(compute_hourly_metrics(df))
    return visualize_forecast(hourly_df, title="Hourly Latency Forecast")

@app.callback(
    Output("latency-anomalies", "figure"),
    Input("refresh", "n_intervals")
)
def update_anomaly_plot(_):
    df = load_trace_data()
    hourly_df = forecast_hourly_latency(compute_hourly_metrics(df))
    return plot_anomaly(hourly_df, threshold=100)

@app.callback(
    Output("btc-price", "figure"),
    Input("refresh", "n_intervals")
)
def update_price_plot(_):
    df = load_trace_data()
    df["price_time"] = df["hour_str"]  # Rename for compatibility
    return plot_price_over_time(df, time_col="price_time", price_col="price_usd")

@app.callback(
    Output("latency-forecast-daily", "figure"),
    Input("refresh", "n_intervals")
)
def update_daily_forecast(_):
    df = load_trace_data()
    daily_df = forecast_daily_latency(compute_daily_metrics(df))
    return visualize_forecast(daily_df, title="Daily Latency Forecast")
