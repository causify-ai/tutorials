# dashboards/dashboard_app.py

import os
import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc, dash_table
from datetime import datetime
from pathlib import Path
import webbrowser
import threading

# ---------- Resolve Paths ----------
BASE_DIR = Path(__file__).resolve().parents[1]
REPORT_DIR = BASE_DIR / "report"

# ---------- Load Data ----------
ewma_df = pd.read_csv(REPORT_DIR / "ewma_anomalies.csv", parse_dates=["window_start"]).sort_values("window_start")
coord_df = pd.read_csv(REPORT_DIR / "coordinated_attacks.csv", parse_dates=["minute"])
forecast_df = pd.read_csv(REPORT_DIR / "prophet_forecast.csv", parse_dates=["ds"])
explain_df = pd.read_csv(REPORT_DIR / "anomaly_explanations_full.csv", parse_dates=["window_start"])

# ---------- Dash Setup ----------
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Bitcoin Anomaly Detection Dashboard"
server = app.server

# ---------- Visualizations ----------

def ewma_graph():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ewma_df["window_start"], y=ewma_df["tx_count_1min"], mode="lines+markers", name="Transaction Count", line=dict(color="blue")))
    fig.add_trace(go.Scatter(x=ewma_df["window_start"], y=ewma_df["ewma"], mode="lines", name="EWMA", line=dict(color="orange", dash="dash")))
    anomalies = ewma_df[ewma_df["is_anomaly"] == 1]
    fig.add_trace(go.Scatter(x=anomalies["window_start"], y=anomalies["tx_count_1min"], mode="markers", name="Anomalies", marker=dict(color="red", size=8)))
    fig.update_layout(title="EWMA Anomaly Detection", xaxis_title="Time", yaxis_title="Transactions per Minute")
    return fig

def zscore_heatmap():
    df = ewma_df.copy()
    df["date"] = df["window_start"].dt.date
    df["hour"] = df["window_start"].dt.hour
    pivot = df.groupby(["date", "hour"])["z_score"].mean().reset_index()
    matrix = pivot.pivot(index="date", columns="hour", values="z_score")
    fig = px.imshow(matrix, color_continuous_scale="RdBu_r", aspect="auto", labels=dict(color="Avg Z-Score"), title="Average Z-Score by Date and Hour")
    return fig

def anomaly_pie():
    dist = ewma_df["is_anomaly"].value_counts(normalize=True).rename({0: "Normal", 1: "Anomaly"})
    fig = px.pie(values=dist.values, names=dist.index, title="Distribution of Anomalous vs Normal Time Windows", color_discrete_sequence=["#66b3ff", "#ff6666"])
    return fig

def anomaly_hour_bar():
    hourly = ewma_df[ewma_df["is_anomaly"] == 1]["window_start"].dt.hour.value_counts().sort_index()
    fig = px.bar(x=hourly.index, y=hourly.values, labels={"x": "Hour (UTC)", "y": "Number of Anomalies"}, title="Anomalies by Hour of Day")
    return fig

def coordinated_attacks():
    fig = px.line(coord_df, x="minute", y="total_flagged", markers=True, title="Coordinated Attack Candidates", labels={"total_flagged": "Flagged Transactions", "minute": "Time"})
    fig.update_traces(marker=dict(size=8, color="purple"))
    return fig

def forecast_plot():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=forecast_df["ds"], y=forecast_df["yhat"], name="Forecast", mode="lines", line=dict(color="green")))
    fig.add_trace(go.Scatter(x=forecast_df["ds"], y=forecast_df["yhat_upper"], name="Upper Bound", mode="lines", showlegend=False))
    fig.add_trace(go.Scatter(x=forecast_df["ds"], y=forecast_df["yhat_lower"], name="Lower Bound", fill="tonexty", mode="lines", fillcolor="rgba(0,200,100,0.2)", showlegend=True))
    fig.update_layout(title="Forecast of Bitcoin Transaction Volume (30-Min Ahead)", xaxis_title="Time", yaxis_title="Transaction Count")
    return fig

def explanation_table():
    return dash_table.DataTable(
        columns=[{"name": "Time", "id": "window_start"}, {"name": "Summary", "id": "explanation"}],
        data=explain_df[["window_start", "explanation"]].to_dict("records"),
        page_size=5,
        style_cell={"textAlign": "left", "whiteSpace": "normal"},
        style_table={"overflowX": "auto"},
    )

# ---------- Layout ----------
app.layout = html.Div([
    html.H1("Real-Time Bitcoin Anomaly Detection Dashboard", style={"textAlign": "center"}),
    dcc.Tabs([
        dcc.Tab(label="Overview", children=[
            html.Br(), dcc.Graph(figure=ewma_graph()),
            html.Br(), dcc.Graph(figure=zscore_heatmap()),
            html.Br(), dcc.Graph(figure=anomaly_pie()),
            html.Br(), dcc.Graph(figure=anomaly_hour_bar())
        ]),
        dcc.Tab(label="Detection & Forecasting", children=[
            html.Br(), dcc.Graph(figure=coordinated_attacks()),
            html.Br(), dcc.Graph(figure=forecast_plot())
        ]),
        dcc.Tab(label="Explanation Audit Trail", children=[
            html.Br(), explanation_table()
        ])
    ])
])

# ---------- Browser Auto-Launch ----------
def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050")

if __name__ == "__main__":
    threading.Timer(1, open_browser).start()
    app.run(debug=True, use_reloader=False, port=8050)
