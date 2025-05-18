import plotly.graph_objs as go
import plotly.io as pio

def _render_plot(fig):
    config = {"displayModeBar": False, "responsive": True}
    return pio.to_html(fig, full_html=False, include_plotlyjs='cdn', config=config)

def plot_btc(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['price'], mode='lines', name='BTC Price', line=dict(color='blue')))
    fig.update_layout(title='Bitcoin Price Over Time', xaxis_title='Time', yaxis_title='USD', template='plotly_white')
    return _render_plot(fig)

def plot_ma(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['price'], mode='lines', name='Price'))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA'], mode='lines', name='MA', line=dict(color='orange')))
    fig.update_layout(title='Moving Average vs Price', xaxis_title='Time', yaxis_title='USD', template='plotly_white')
    return _render_plot(fig)

def plot_anomalies(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['price'], mode='lines', name='BTC Price'))
    anomalies = df[df['anomaly']]
    fig.add_trace(go.Scatter(x=anomalies.index, y=anomalies['price'], mode='markers', name='Anomaly', marker=dict(color='red', size=6)))
    fig.update_layout(title='Anomaly Detection', xaxis_title='Time', yaxis_title='USD', template='plotly_white')
    return _render_plot(fig)

def plot_ma_comparison(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['price'], mode='lines', name='Price'))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA_7'], mode='lines', name='MA_7'))
    fig.add_trace(go.Scatter(x=df.index, y=df['MA_30'], mode='lines', name='MA_30'))
    fig.update_layout(title='Short vs Long-Term Moving Averages', xaxis_title='Time', yaxis_title='USD', template='plotly_white')
    return _render_plot(fig)

def plot_ema(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['price'], mode='lines', name='Price'))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_12'], mode='lines', name='EMA_12'))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_26'], mode='lines', name='EMA_26'))
    fig.update_layout(title='Exponential Moving Averages', xaxis_title='Time', yaxis_title='USD', template='plotly_white')
    return _render_plot(fig)

def plot_macd(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], mode='lines', name='MACD'))
    fig.add_trace(go.Scatter(x=df.index, y=df['Signal'], mode='lines', name='Signal'))
    fig.update_layout(title='MACD vs Signal Line', xaxis_title='Time', yaxis_title='MACD', template='plotly_white')
    return _render_plot(fig)

def plot_returns(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Returns'], mode='lines', name='Returns', line=dict(color='purple')))
    fig.update_layout(title='Hourly Returns', xaxis_title='Time', yaxis_title='Return %', template='plotly_white')
    return _render_plot(fig)

def plot_cumulative_returns(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Cumulative_Return'], mode='lines', name='Cumulative Return', line=dict(color='green')))
    fig.update_layout(title='Cumulative Returns Over Time', xaxis_title='Time', yaxis_title='Growth Factor', template='plotly_white')
    return _render_plot(fig)

def plot_price_change(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Price_Change'], mode='lines', name='Price Change', line=dict(color='orange')))
    fig.update_layout(title='Price Change per Hour', xaxis_title='Time', yaxis_title='Change (USD)', template='plotly_white')
    return _render_plot(fig)

def plot_volatility(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Volatility'], mode='lines', name='Volatility', line=dict(color='red')))
    fig.update_layout(title='Rolling Volatility (10-Hour Std Dev)', xaxis_title='Time', yaxis_title='Volatility', template='plotly_white')
    return _render_plot(fig)
