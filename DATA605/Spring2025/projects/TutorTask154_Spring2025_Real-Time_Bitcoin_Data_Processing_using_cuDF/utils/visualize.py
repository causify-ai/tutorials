import plotly.graph_objects as go

def plot_all(gdf):
    pdf = gdf.to_pandas()
    
    fig = go.Figure()

    # Plot Bitcoin Price
    fig.add_trace(go.Scatter(x=pdf["timestamp"], y=pdf["price"], mode="lines+markers", name="Bitcoin Price"))

    # Plot SMA if exists
    if "SMA" in pdf.columns:
        fig.add_trace(go.Scatter(x=pdf["timestamp"], y=pdf["SMA"],mode="lines", name="Simple Moving Average (SMA)", line=dict(dash='dash')))

    # Plot Volatility if exists
    if "Volatility" in pdf.columns:
        fig.add_trace(go.Scatter(x=pdf["timestamp"], y=pdf["Volatility"], mode="lines", name="Volatility", line=dict(dash='dot')))

    # Plot Rate of Change if exists
    if "Rate_of_Change" in pdf.columns:
        fig.add_trace(go.Scatter(x=pdf["timestamp"], y=pdf["Rate_of_Change"], mode="lines", name="Rate of Change", line=dict(dash='longdash')))

    # Update layout
    fig.update_layout(
        title="Bitcoin Price with SMA, Volatility, and Rate of Change",
        xaxis_title="Timestamp",
        yaxis_title="Value",
        legend_title="Legend",
        template="plotly_dark",
        hovermode="x unified",
        width=1200,
        height=700
    )

    fig.show()