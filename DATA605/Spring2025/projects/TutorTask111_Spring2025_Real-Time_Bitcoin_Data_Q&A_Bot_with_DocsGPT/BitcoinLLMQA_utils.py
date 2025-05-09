import requests 
import pandas as pd
from datetime import datetime
import numpy as np
from dotenv import load_dotenv
from llama_cpp import Llama


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

load_dotenv()

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
CSV_FILENAME = 'bitcoin_prices.csv'

# -----------------------------------------------------------------------------
# Data Handling & Updates
# -----------------------------------------------------------------------------

def fetch_bitcoin_price():
    """Fetch current Bitcoin price from CoinGecko API"""
    try:
        response = requests.get(COINGECKO_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data['bitcoin']['usd']
    except Exception as e:
        print(f"API Error: {e}")
        return None

def update_dataset(new_price):
    """Update CSV with new price and calculate rolling volatility, avoiding duplicates."""
    now = datetime.now().replace(microsecond=0)
    new_entry = pd.DataFrame([{
        'timestamp': now,
        'price': new_price,
        'volatility': np.nan
    }])
    try:
        df = pd.read_csv(CSV_FILENAME, parse_dates=['timestamp'])
    except FileNotFoundError:
        df = new_entry
    df['log_returns'] = np.log(df['price'] / df['price'].shift(1))
    df['volatility'] = df['log_returns'].rolling(12).std() * np.sqrt(12)
    df.drop(columns=['log_returns'], inplace=True)
    df['volatility'] = df['volatility'].fillna('')
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
    df.to_csv(CSV_FILENAME, index=False)
    print(f"Saved price: {new_price} | Volatility: {df['volatility'].iloc[-1]}")
    return df

# -----------------------------------------------------------------------------
# Analysis & Trends
# -----------------------------------------------------------------------------

def analyze_data(df):
    """Generate key metrics from the dataset"""
    try:
        df['volatility'] = pd.to_numeric(df['volatility'], errors='coerce')
        df['volatility'] = df['volatility'].fillna(0)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        hourly_avg = df.resample('h', on='timestamp').mean(numeric_only=True)
        daily_volatility = df.resample('D', on='timestamp').std(numeric_only=True)
        recent_anomalies = df[
            df['volatility'].apply(lambda x: float(x) if x != '' else np.nan) >
            df['volatility'].astype(float).quantile(0.95)
        ]
        return {
            'hourly_avg': hourly_avg,
            'daily_volatility': daily_volatility,
            'recent_anomalies': recent_anomalies
        }
    except Exception as e:
        print(f"Analysis error: {e}")
        return None

def setup_docsgpt():
    model_path = "llama-2-7b-chat.Q4_K_M.gguf"
    return Llama(
        model_path=model_path,
        n_ctx=2048,
        n_threads=6,
        n_gpu_layers=1
    )

def handle_query(llm, question):
    prompt = f"### User: {question}\n### Assistant:"
    response = llm(
        prompt,
        max_tokens=200,
        stop=["\n", "###"],
        temperature=0.7
    )
    return response['choices'][0]['text'].strip()


def demonstrate_coingecko_api():
    """Demonstrates direct API call vs wrapper function"""
    try:
        response = requests.get(COINGECKO_URL, timeout=10)
        response.raise_for_status()
        raw_data = response.json()
        current_price = raw_data['bitcoin']['usd']
        return current_price, raw_data
    except Exception as e:
        return None, {"error": str(e)}

def load_dataset(filename=CSV_FILENAME):
    """Load Bitcoin dataset with proper data types"""
    try:
        df = pd.read_csv(filename)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['volatility'] = pd.to_numeric(df['volatility'], errors='coerce')
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=['timestamp', 'price', 'volatility'])
    
# -----------------------------------------------------------------------------
# Visualization
# -----------------------------------------------------------------------------

def visualize_bitcoin_data(df, periods=48):
    """Create standardized price and volatility charts
    
    Args:
        df: DataFrame with Bitcoin data
        periods: Number of recent records to display
        
    Returns:
        matplotlib figure object
    """
    import matplotlib.pyplot as plt
    
    fig, ax = plt.subplots(2, 1, figsize=(10, 6))
    
    # Ensure timestamp is datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Price chart
    df.set_index('timestamp')['price'].tail(periods).plot(
        ax=ax[0], 
        title='Bitcoin Price (Last 48 Records)'
    )
    ax[0].set_ylabel('USD')
    
    # Volatility chart
    df.set_index('timestamp')['volatility'].tail(periods).plot(
        ax=ax[1], 
        title='Rolling Volatility', 
        color='orange'
    )
    ax[1].set_ylabel('Volatility')
    
    plt.tight_layout()
    return fig

def get_price_trends(df, period='24h'):
    """Calculate price trends over specified period
    
    Args:
        df: DataFrame with Bitcoin data
        period: '24h', '7d', etc.
        
    Returns:
        Dictionary with trend metrics
    """
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    if period == '24h':
        cutoff = datetime.now() - pd.Timedelta(hours=24)
    elif period == '7d':
        cutoff = datetime.now() - pd.Timedelta(days=7)
    else:
        cutoff = datetime.now() - pd.Timedelta(hours=6)
    
    recent_df = df[df['timestamp'] >= cutoff]
    
    if len(recent_df) < 2:
        return {"error": "Not enough data points for the selected period"}
    
    start_price = recent_df['price'].iloc[0]
    end_price = recent_df['price'].iloc[-1]
    pct_change = ((end_price - start_price) / start_price) * 100
    
    return {
        "start_price": start_price,
        "end_price": end_price,
        "pct_change": pct_change,
        "max_price": recent_df['price'].max(),
        "min_price": recent_df['price'].min(),
        "period": period
    }
