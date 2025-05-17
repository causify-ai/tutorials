# visualization/price_dashboard.py

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from analysis.time_series_analysis import compute_moving_average, detect_price_anomalies
from analysis.time_series_analysis import fetch_time_series_from_db

TEMPLATE_THEME = "plotly_dark"
px.defaults.template = TEMPLATE_THEME


def plot_price(df):
    return px.line(
        df,
        x="timestamp",
        y="price",
        title="Bitcoin Price Over Time",
        template=TEMPLATE_THEME,
    )


def plot_moving_average(df, window=10):
    df_ma = compute_moving_average(df, window)
    return px.line(
        df_ma,
        x="timestamp",
        y="moving_avg",
        title=f"{window}-Day Moving Average",
        template=TEMPLATE_THEME,
    )


def plot_anomalies(df, window=10, threshold=2.0):
    df_anom = detect_price_anomalies(df, window, threshold)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_anom["timestamp"], y=df_anom["price"], mode="lines", name="Price"
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_anom.loc[df_anom["anomaly"], "timestamp"],
            y=df_anom.loc[df_anom["anomaly"], "price"],
            mode="markers",
            name="Anomalies",
            marker=dict(size=8),
        )
    )
    fig.update_layout(
        title=f"Anomalies (±{threshold}σ)",
        xaxis_title="Timestamp",
        yaxis_title="Price (USD)",
        template=TEMPLATE_THEME,
    )
    return fig


def plot_dashboard(df, window=10, threshold=2.0):
    """
    Build a 3-panel dashboard: price, moving average, anomalies.

    Args:
        df: DataFrame with analytics columns.
        window: Rolling window used.
        threshold: Anomaly threshold.

    Returns:
        Plotly Figure ready to write_html().
    """
    fig1 = plot_price(df)
    fig2 = plot_moving_average(df, window)
    fig3 = plot_anomalies(df, window, threshold)
    dash = make_subplots(
        rows=3,
        cols=1,
        subplot_titles=["Price", "Moving Average", "Anomalies"],
        vertical_spacing=0.1,
    )
    for t in fig1.data:
        dash.add_trace(t, row=1, col=1)
    for t in fig2.data:
        dash.add_trace(t, row=2, col=1)
    for t in fig3.data:
        dash.add_trace(t, row=3, col=1)
    dash.update_layout(
        height=1200,
        title_text="Bitcoin Price Dashboard",
        template=TEMPLATE_THEME,
    )
    return dash
