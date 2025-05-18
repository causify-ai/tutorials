import plotly.graph_objs as go
import plotly.io as pio

def _render_plot(fig):
    config = {
        "displayModeBar": True,
        "responsive": True,
        "scrollZoom": True,
        "displaylogo": False,
        "modeBarButtonsToRemove": ["zoomIn2d", "zoomOut2d", "resetScale2d"]
    }
    fig.update_layout(
        template='plotly_dark',
        font=dict(family='Segoe UI', size=13),
        hovermode='x unified',
        dragmode='pan',
        margin=dict(t=60, l=50, r=30, b=60),
        height=500,
        legend=dict(x=0.01, y=0.99),
        xaxis=dict(showgrid=True, title='Time'),
        yaxis=dict(showgrid=True, title='Value'),
    )
    return pio.to_html(fig, full_html=False, include_plotlyjs='cdn', config=config)

def plot_btc(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=df['price'],
        mode='lines+markers',
        name='BTC Price',
        line=dict(color='cyan', width=2),
        marker=dict(size=4)
    ))
    fig.update_layout(title='📈 Live Bitcoin Price', yaxis_title='Price (USD)')
    return _render_plot(fig)

def plot_ma(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['price'], mode='lines', name='Price', line=dict(color='royalblue', width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA'], mode='lines', name='SMA', line=dict(color='orange', width=2, dash='dot')))
    fig.update_layout(title='📊 Price vs Simple Moving Average (SMA)', yaxis_title='Price (USD)')
    return _render_plot(fig)

def plot_anomalies(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['price'], mode='lines', name='BTC Price', line=dict(color='lightblue')))
    anomalies = df[df['anomaly']]
    fig.add_trace(go.Scatter(
        x=anomalies.index, y=anomalies['price'],
        mode='markers',
        name='Anomaly',
        marker=dict(color='red', size=8, symbol='x')
    ))
    fig.update_layout(title='🚨 Anomalies in Bitcoin Price', yaxis_title='Price (USD)')
    return _render_plot(fig)

def plot_ma_comparison(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['price'], mode='lines', name='Price', line=dict(color='white')))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA_7'], mode='lines', name='7-Hour MA', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA_30'], mode='lines', name='30-Hour MA', line=dict(color='magenta')))
    fig.update_layout(title='⏱️ Short-Term vs Long-Term Moving Averages', yaxis_title='Price (USD)')
    return _render_plot(fig)

def plot_ema(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_12'], mode='lines', name='EMA 12', line=dict(color='dodgerblue', width=2)))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_26'], mode='lines', name='EMA 26', line=dict(color='tomato', width=2, dash='dot')))
    fig.update_layout(title='📉 Exponential Moving Averages (EMA 12 vs 26)', yaxis_title='Price (USD)')
    return _render_plot(fig)

def plot_macd(df):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df.index, y=df['MACD'], name='MACD', marker_color='steelblue'))
    fig.add_trace(go.Scatter(x=df.index, y=df['Signal'], mode='lines', name='Signal', line=dict(color='gold', width=2)))
    fig.update_layout(title='📊 MACD Histogram & Signal Line', yaxis_title='MACD Value')
    return _render_plot(fig)

def plot_returns(df):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df.index, y=df['Returns'], name='Returns', marker_color='mediumpurple'))
    fig.update_layout(title='🔄 Hourly Return Fluctuations', yaxis_title='Return (%)')
    return _render_plot(fig)

def plot_cumulative_returns(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Cumulative_Return'], mode='lines', name='Cumulative Return', line=dict(color='lime', width=2)))
    fig.update_layout(title='📈 Cumulative Return Growth Over Time', yaxis_title='Growth Factor')
    return _render_plot(fig)

def plot_price_change(df):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df.index, y=df['Price_Change'], name='Price Change', marker_color='darkorange'))
    fig.update_layout(title='📉 Hourly Price Change (USD)', yaxis_title='Change ($)')
    return _render_plot(fig)

def plot_volatility(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Volatility'], name='Volatility', fill='tozeroy', line=dict(color='crimson', width=2)))
    fig.update_layout(title='🌪️ Rolling Volatility (10-Hour Std Dev)', yaxis_title='Volatility')
    return _render_plot(fig)

def plot_forecast_interactive(forecast_df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=forecast_df['ds'], y=forecast_df['yhat'], mode='lines', name='Forecast',
        line=dict(color='deepskyblue', width=2),
        hovertemplate='%{x|%b %d %H:%M}<br>Forecast: %{y:.2f} USD<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=forecast_df['ds'], y=forecast_df['yhat_upper'], mode='lines', name='Upper Bound',
        line=dict(dash='dot', color='lightgray'),
        hovertemplate='Upper: %{y:.2f}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=forecast_df['ds'], y=forecast_df['yhat_lower'], mode='lines', name='Lower Bound',
        line=dict(dash='dot', color='lightgray'),
        fill='tonexty', fillcolor='rgba(173,216,230,0.2)',
        hovertemplate='Lower: %{y:.2f}<extra></extra>'
    ))
    fig.update_layout(title='🔮 Forecasted Bitcoin Price with Confidence Bounds', yaxis_title='Forecasted Price (USD)')
    return _render_plot(fig)