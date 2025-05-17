import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import plotly.graph_objs as go
import pandas as pd
from storage.db_handler import get_db, init_db
from datetime import datetime, timedelta
import json
import os
from flask import Flask, send_from_directory
from crypto.encrypt import decrypt_data, sender_private, recipient_private

# Get the absolute path to the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Create Flask app
server = Flask(__name__, static_folder=os.path.join(PROJECT_ROOT, 'static'))

# Serve static files
@server.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(os.path.join(PROJECT_ROOT, 'static'), path)

# Create Dash app
app = dash.Dash(__name__, server=server)
app.config.suppress_callback_exceptions = True

def ensure_db_initialized():
    """Ensure database and tables are initialized"""
    try:
        init_db()
        with get_db() as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='btc_analysis'")
            if not cursor.fetchone():
                print("❌ Database tables not properly initialized. Please run main.py first to collect some data.")
                return False
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

def fetch_analysis_data():
    """Fetch analysis data from SQLite"""
    if not ensure_db_initialized():
        return pd.DataFrame()
        
    try:
        with get_db() as conn:
            cursor = conn.execute("""
                SELECT timestamp, price, MA_5, MA_10, Volatility_5, Returns 
                FROM btc_analysis 
                ORDER BY timestamp
            """)
            rows = cursor.fetchall()
            
        if not rows:
            return pd.DataFrame()
            
        df = pd.DataFrame(rows, columns=['timestamp', 'price', 'MA_5', 'MA_10', 'Volatility_5', 'Returns'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        print(f"❌ Error fetching analysis data: {e}")
        return pd.DataFrame()

def fetch_forecast_data():
    """Fetch forecast data from SQLite"""
    if not ensure_db_initialized():
        return pd.DataFrame()
        
    try:
        with get_db() as conn:
            cursor = conn.execute("""
                SELECT timestamp, predicted_price 
                FROM btc_forecast 
                ORDER BY timestamp
            """)
            rows = cursor.fetchall()
            
        if not rows:
            return pd.DataFrame()
            
        df = pd.DataFrame(rows, columns=['timestamp', 'predicted_price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        print(f"❌ Error fetching forecast data: {e}")
        return pd.DataFrame()

def fetch_candlestick_data():
    """Fetch candlestick data from SQLite"""
    if not ensure_db_initialized():
        return pd.DataFrame()
        
    try:
        # Get data from the last 100 minutes
        with get_db() as conn:
            cursor = conn.execute("""
                SELECT timestamp, encrypted_price 
                FROM btc_price 
                WHERE timestamp >= datetime('now', '-100 minutes')
                ORDER BY timestamp
            """)
            rows = cursor.fetchall()
            
        if not rows:
            return pd.DataFrame()
            
        # Decrypt the prices
        data = []
        for ts, enc_price in rows:
            try:
                price = float(decrypt_data(enc_price, sender_private.public_key, recipient_private))
                print(f"Decrypted and plotted Candlestick: {ts} with {price}")
                data.append((ts, price))
            except Exception as e:
                print(f"⚠️ Error decrypting price: {e}")
                continue
                
        if not data:
            return pd.DataFrame()
            
        df = pd.DataFrame(data, columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        
        # Resample to 1-minute candles
        ohlc = df.resample('1min').agg({
            'price': ['first', 'max', 'min', 'last']
        })
        
        # Rename columns
        ohlc.columns = ['open', 'high', 'low', 'close']
        ohlc = ohlc.dropna()
        
        return ohlc
    except Exception as e:
        print(f"❌ Error fetching candlestick data: {e}")
        return pd.DataFrame()

def ensure_plot_directory():
    """Ensure the plots directory exists"""
    plot_dir = os.path.join(PROJECT_ROOT, 'static', 'plots')
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)
    return plot_dir

def get_latest_plots():
    """Get the latest plot paths from the JSON file"""
    try:
        plot_file = os.path.join(ensure_plot_directory(), 'latest_plots.json')
        if os.path.exists(plot_file):
            with open(plot_file, 'r') as f:
                plots = json.load(f)
                # Verify that all plot files exist
                for key in ['price_ma', 'volatility', 'returns', 'forecast']:
                    if key in plots and plots[key]:
                        plot_path = os.path.join(PROJECT_ROOT, 'static', 'plots', plots[key])
                        if not os.path.exists(plot_path):
                            print(f"⚠️ Plot file not found: {plot_path}")
                            plots[key] = None
                return plots
    except Exception as e:
        print(f"Error reading plot paths: {e}")
    return None

# Dashboard layout
app.layout = html.Div([
    html.H1('PyNaCl - BTCUSDT Live Analysis Dashboard', style={'textAlign': 'center'}),
    html.H3('Dhanush Vasa (UID:121227645)', style={'textAlign': 'center'}),
    
    dcc.Interval(
        id='interval-component',
        interval=10*1000,  # Update every 10 seconds
        n_intervals=0
    ),
    
    # Candlestick chart
    html.Div([
        html.H2('Live Candlestick Chart', style={'textAlign': 'center', 'padding-top': '10px'}),
        html.P('Real-time price data with 1-minute candles', style={'textAlign': 'center', 'color': 'gray'}),
        dcc.Graph(id='candlestick-graph', style={'height': '600px'})
    ]),
    
    # Hourly analysis
    html.Div([
        html.H2('Hourly Analysis and Forecast', style={'textAlign': 'center', 'padding-top': '10px'}),
        html.P('Updated every hour with technical indicators and price predictions', style={'textAlign': 'center', 'color': 'gray'}),
        dcc.Graph(id='live-graph')
    ]),
    
    # Analysis plots
    html.Div([
        html.H2('Analysis Results', style={'textAlign': 'center', 'padding-top': '10px'}),
        html.P('Detailed analysis plots updated hourly', style={'textAlign': 'center', 'color': 'gray'}),
        html.Div([
            html.Div([
                html.H3('Price and Moving Averages'),
                html.Img(id='price-ma-plot', style={'width': '100%', 'height': 'auto'})
            ], className='six columns'),
            html.Div([
                html.H3('Volatility'),
                html.Img(id='volatility-plot', style={'width': '100%', 'height': 'auto'})
            ], className='six columns')
        ], className='row'),
        html.Div([
            html.Div([
                html.H3('Returns'),
                html.Img(id='returns-plot', style={'width': '100%', 'height': 'auto'})
            ], className='six columns'),
            html.Div([
                html.H3('Price Forecast'),
                html.Img(id='forecast-plot', style={'width': '100%', 'height': 'auto'})
            ], className='six columns')
        ], className='row')
    ])
])

@app.callback(
    [Output('candlestick-graph', 'figure'),
     Output('live-graph', 'figure'),
     Output('price-ma-plot', 'src'),
     Output('volatility-plot', 'src'),
     Output('returns-plot', 'src'),
     Output('forecast-plot', 'src')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    print(f"[{datetime.now()}] Update dashboard called with n = {n}")
    
    # Get candlestick data
    df_candles = fetch_candlestick_data()
    
    # Create candlestick chart
    candlestick = go.Figure()
    if not df_candles.empty:
        candlestick.add_trace(go.Candlestick(
            x=df_candles.index,
            open=df_candles['open'],
            high=df_candles['high'],
            low=df_candles['low'],
            close=df_candles['close'],
            name='BTCUSDT'
        ))
        
        # Add moving averages
        candlestick.add_trace(go.Scatter(
            x=df_candles.index,
            y=df_candles['close'].rolling(window=5).mean(),
            name='MA5',
            line=dict(color='orange')
        ))
        candlestick.add_trace(go.Scatter(
            x=df_candles.index,
            y=df_candles['close'].rolling(window=10).mean(),
            name='MA10',
            line=dict(color='blue')
        ))
        
        candlestick.update_layout(
            title='BTCUSDT 1-Minute Candlestick Chart',
            yaxis_title='Price (USD)',
            xaxis_title='Time',
            template='plotly_white',
            xaxis_rangeslider_visible=False,
            height=600,
            uirevision='constant'
        )
    
    # Get hourly analysis data
    df_analysis = fetch_analysis_data()
    df_forecast = fetch_forecast_data()

    # Create hourly analysis graph
    traces = []
    if not df_analysis.empty:
        traces.append(go.Scatter(
            x=df_analysis['timestamp'], y=df_analysis['price'],
            mode='lines', name='Price', line=dict(color='blue')
        ))
        if 'MA_5' in df_analysis.columns:
            traces.append(go.Scatter(
                x=df_analysis['timestamp'], y=df_analysis['MA_5'],
                mode='lines', name='5-min MA', line=dict(color='orange')
            ))
        if 'MA_10' in df_analysis.columns:
            traces.append(go.Scatter(
                x=df_analysis['timestamp'], y=df_analysis['MA_10'],
                mode='lines', name='10-min MA', line=dict(color='green')
            ))

    if not df_forecast.empty:
        traces.append(go.Scatter(
            x=df_forecast['timestamp'], y=df_forecast['predicted_price'],
            mode='lines+markers', name='Forecast', line=dict(color='purple', dash='dash')
        ))

    figure = {
        'data': traces,
        'layout': go.Layout(
            title='Hourly Analysis with Technical Indicators and Forecast',
            xaxis=dict(title='Time'),
            yaxis=dict(title='Price (USD)'),
            uirevision='constant',
            margin=dict(l=40, r=20, t=60, b=30),
            legend=dict(x=0, y=1),
            template='plotly_white'
        )
    }

    # Get latest analysis plots
    plots = get_latest_plots()
    if plots:
        # Add timestamp to prevent caching
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return (
            candlestick,
            figure,
            f'/static/plots/{plots["price_ma"]}?t={timestamp}' if plots["price_ma"] else None,
            f'/static/plots/{plots["volatility"]}?t={timestamp}' if plots["volatility"] else None,
            f'/static/plots/{plots["returns"]}?t={timestamp}' if plots["returns"] else None,
            f'/static/plots/{plots["forecast"]}?t={timestamp}' if plots["forecast"] else None
        )
    
    return candlestick, figure, None, None, None, None

if __name__ == '__main__':
    print(f"[{datetime.now()}] Starting dashboard...")
    print("Make sure main.py and analysis.run_hourly_analysis are running!")
    # Ensure plot directory exists
    ensure_plot_directory()
    print(f"Static files will be served from: {os.path.join(PROJECT_ROOT, 'static')}")
    app.run(debug=False, host='0.0.0.0', port=8050, use_reloader=False)
