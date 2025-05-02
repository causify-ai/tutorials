import duckdb
import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import plotly.graph_objs as go
import pandas as pd

# Create Dash app
app = dash.Dash(__name__)
server = app.server  # Expose server if needed for deployment

def fetch_analysis_data():
    conn = duckdb.connect("btc_data.duckdb", read_only=True)
    df = conn.execute("""
        SELECT * FROM btc_analysis ORDER BY timestamp
    """).fetchdf()
    conn.close()
    return df

def fetch_forecast_data():
    conn = duckdb.connect("btc_data.duckdb", read_only=True)
    df = conn.execute("""
        SELECT * FROM btc_forecast ORDER BY timestamp
    """).fetchdf()
    conn.close()
    return df

# Dashboard layout
app.layout = html.Div([
    html.H1('BTCUSDT Live Analysis Dashboard', style={'textAlign': 'center'}),
    
    dcc.Interval(
        id='interval-component',
        interval=10*1000,  # Update every 10 seconds
        n_intervals=0
    ),
    
    dcc.Graph(id='live-graph')
])

@app.callback(
    Output('live-graph', 'figure'),
    Input('interval-component', 'n_intervals')
)

def update_graph(n):
    print(f"Update graph called with n = {n}")
    
    df_analysis = fetch_analysis_data()
    df_forecast = fetch_forecast_data()

    traces = []

    if not df_analysis.empty:
        traces.append(go.Scatter(
            x=df_analysis['timestamp'], y=df_analysis['price'],
            mode='lines', name='Price', line=dict(color='blue')
        ))
        traces.append(go.Scatter(
            x=df_analysis['timestamp'], y=df_analysis['MA_5'],
            mode='lines', name='5-min MA', line=dict(color='orange')
        ))
        traces.append(go.Scatter(
            x=df_analysis['timestamp'], y=df_analysis['MA_10'],
            mode='lines', name='10-min MA', line=dict(color='green')
        ))
        traces.append(go.Scatter(
            x=df_analysis['timestamp'], y=df_analysis['Volatility_5'],
            mode='lines', name='Volatility', line=dict(color='red')
        ))

    if not df_forecast.empty:
        traces.append(go.Scatter(
            x=df_forecast['timestamp'], y=df_forecast['predicted_price'],
            mode='lines+markers', name='Forecast', line=dict(color='purple', dash='dash')
        ))

    figure = {
        'data': traces,
        'layout': go.Layout(
            title='BTC Price, Indicators and Forecast',
            xaxis=dict(title='Time'),
            yaxis=dict(title='Price (USD)'),
            uirevision='constant',
            margin=dict(l=40, r=20, t=60, b=30),
            legend=dict(x=0, y=1),
            template='plotly_white'
        )
    }

    return figure

if __name__ == '__main__':
    app.run(debug=False, port=8050, use_reloader=False)
