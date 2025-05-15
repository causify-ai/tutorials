import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from analysis.time_series_analysis import (
    fetch_time_series_from_db,
    compute_moving_averages,
    detect_price_anomalies,
    compute_bollinger_bands,
    compute_daily_returns,
    compute_rolling_stats,
    forecast_with_prophet,
)


# TEMPLATE_THEME = "plotly_dark"
TEMPLATE_THEME = "plotly"
px.defaults.template = TEMPLATE_THEME


def plot_price(df):
    return px.line(
        df,
        x="timestamp",
        y="price",
        title="Bitcoin Price Over Time",
        template=TEMPLATE_THEME,
    )


def plot_moving_averages(df, days=[7, 30]):
    df_ma = compute_moving_averages(df, days)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=df_ma["timestamp"], y=df_ma["price"], mode="lines", name="Price")
    )
    for d in days:
        fig.add_trace(
            go.Scatter(
                x=df_ma["timestamp"],
                y=df_ma[f"moving_average_{d}d"],
                mode="lines",
                name=f"{d}-Day MA",
            )
        )
    fig.update_layout(title="Moving Averages", template=TEMPLATE_THEME)
    return fig


def plot_anomalies(df, days=[7], threshold=2.0):
    df_anom = detect_price_anomalies(df, days, threshold)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_anom["timestamp"], y=df_anom["price"], mode="lines", name="Price"
        )
    )
    for d in days:
        mask = df_anom[f"anomaly_{d}d"]
        fig.add_trace(
            go.Scatter(
                x=df_anom.loc[mask, "timestamp"],
                y=df_anom.loc[mask, "price"],
                mode="markers",
                name=f"Anomalies ({d}d ±{threshold}σ)",
                marker=dict(size=8),
            )
        )
    fig.update_layout(title="Price Anomalies", template=TEMPLATE_THEME)
    return fig


def plot_bollinger_bands(df, window=168):
    df_bb = compute_bollinger_bands(df, window)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_bb["timestamp"], y=df_bb["price"], name="Price"))
    fig.add_trace(
        go.Scatter(
            x=df_bb["timestamp"],
            y=df_bb["bb_upper"],
            name="Upper Band",
            line=dict(dash="dot"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_bb["timestamp"],
            y=df_bb["bb_lower"],
            name="Lower Band",
            line=dict(dash="dot"),
        )
    )
    fig.update_layout(title="Bollinger Bands", template=TEMPLATE_THEME)
    return fig


def plot_daily_returns(df):
    df_ret = compute_daily_returns(df)
    return px.line(
        df_ret,
        x="timestamp",
        y="daily_return",
        title="Daily Returns (%)",
        template=TEMPLATE_THEME,
    )


def plot_prophet_forecast(df, periods=30):
    """
    Forecast with Prophet and plot the results.
    """

    try:
        forecast = forecast_with_prophet(df, periods=periods)
    except ValueError as e:
        print(f"⚠️ Prophet forecast skipped: {e}")
        return go.Figure()  # Return empty plot to avoid dashboard failure

    fig = go.Figure()

    # Actual data
    fig.add_trace(
        go.Scatter(x=df["timestamp"], y=df["price"], name="Actual", mode="lines")
    )

    # Forecasted trend
    fig.add_trace(
        go.Scatter(x=forecast["ds"], y=forecast["yhat"], name="Forecast", mode="lines")
    )

    # Confidence intervals
    fig.add_trace(
        go.Scatter(
            x=forecast["ds"],
            y=forecast["yhat_upper"],
            name="Upper Bound",
            mode="lines",
            line=dict(width=0),
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=forecast["ds"],
            y=forecast["yhat_lower"],
            name="Lower Bound",
            mode="lines",
            fill="tonexty",
            fillcolor="rgba(0,100,80,0.2)",
            showlegend=False,
        )
    )

    fig.update_layout(title="Bitcoin Forecast (Prophet)", template="plotly_dark")
    return fig


# def plot_arima_forecast(df, steps=30):
#     """
#     Forecast with ARIMA and plot the results.
#     """
#     from analysis.time_series_analysis import forecast_with_arima

#     df_daily = df.set_index("timestamp").resample("D").mean().dropna()
#     forecast = forecast_with_arima(df_daily, steps=steps)

#     last_timestamp = df_daily.index[-1]
#     forecast_index = pd.date_range(
#         start=last_timestamp + pd.Timedelta(days=1), periods=steps
#     )

#     fig = go.Figure()
#     fig.add_trace(
#         go.Scatter(x=df_daily.index, y=df_daily["price"], name="Actual", mode="lines")
#     )
#     fig.add_trace(
#         go.Scatter(x=forecast_index, y=forecast, name="ARIMA Forecast", mode="lines")
#     )

#     fig.update_layout(title="Bitcoin Forecast (ARIMA)", template="plotly_dark")
#     return fig


def plot_dashboard(df, days=[7, 30], threshold=2.0, bb_window=168, forecast_days=30):
    fig1 = plot_price(df)
    fig2 = plot_moving_averages(df, days)
    fig3 = plot_anomalies(df, days, threshold)
    fig4 = plot_bollinger_bands(df, window=bb_window)
    fig5 = plot_daily_returns(df)
    fig6 = plot_prophet_forecast(df, periods=forecast_days)
    # fig7 = plot_arima_forecast(df, steps=forecast_days)

    dash = make_subplots(
        rows=7,
        cols=1,
        subplot_titles=[
            "Price",
            "Moving Averages",
            "Anomalies",
            "Bollinger Bands",
            "Daily Returns",
            "Prophet Forecast",
            # "ARIMA Forecast",
        ],
        vertical_spacing=0.08,
    )

    for fig, row in zip([fig1, fig2, fig3, fig4, fig5, fig6], range(1, 7)):
        for t in fig.data:
            dash.add_trace(t, row=row, col=1)

    dash.update_layout(
        height=2400,
        title_text="📊 Bitcoin Price Analysis + Forecast Dashboard",
        template="plotly",
        # template="plotly_dark",
    )
    return dash
