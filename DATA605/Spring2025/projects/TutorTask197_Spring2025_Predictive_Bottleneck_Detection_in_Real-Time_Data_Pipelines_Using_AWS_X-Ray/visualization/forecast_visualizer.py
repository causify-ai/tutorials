import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots


def visualize_forecast(df, title="Predicted Latency with Confidence Interval"):
    df = df.copy()
    df["ds"] = pd.to_datetime(df["ds"])

    fig = make_subplots(specs=[[{"secondary_y": False}]])

    fig.add_trace(go.Scatter(
        x=df["ds"], y=df["yhat"],
        mode="lines", name="Predicted Latency (ms)",
        line=dict(color="royalblue")
    ))

    fig.add_trace(go.Scatter(
        x=pd.concat([df["ds"], df["ds"][::-1]]),
        y=pd.concat([df["yhat_upper"], df["yhat_lower"][::-1]]),
        fill="toself",
        fillcolor="rgba(173, 216, 230, 0.3)",
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip",
        name="95% Confidence Interval"
    ))

    if "y" in df.columns:
        fig.add_trace(go.Scatter(
            x=df["ds"], y=df["y"],
            mode="lines+markers", name="Actual Latency",
            line=dict(color="gray", dash="dot")
        ))

    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title="Latency (ms)",
        template="plotly_white",
        hovermode="x unified"
    )

    return fig


def plot_price_over_time(df, time_col="hour_str", price_col="price_usd"):
    df = df.copy()
    df[time_col] = pd.to_datetime(df[time_col])

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[time_col], y=df[price_col],
        mode="lines", name="Bitcoin Price (USD)",
        line=dict(color="green")
    ))

    fig.update_layout(
        title="Bitcoin Price Over Time",
        xaxis_title="Time",
        yaxis_title="Price (USD)",
        template="plotly_white",
        hovermode="x unified"
    )

    return fig


def plot_anomaly(df, threshold=100):
    df = df.copy()
    df["ds"] = pd.to_datetime(df["ds"])
    df["anomaly"] = df["yhat"] > threshold

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["ds"], y=df["yhat"],
        mode="lines", name="Predicted Latency",
        line=dict(color="royalblue")
    ))

    anomalies = df[df["anomaly"]]
    fig.add_trace(go.Scatter(
        x=anomalies["ds"], y=anomalies["yhat"],
        mode="markers", name="Anomalies",
        marker=dict(color="red", size=8, symbol="x")
    ))

    fig.update_layout(
        title=f"Latency Anomalies (Threshold > {threshold}ms)",
        xaxis_title="Time",
        yaxis_title="Latency (ms)",
        template="plotly_white",
        hovermode="x unified"
    )

    return fig
