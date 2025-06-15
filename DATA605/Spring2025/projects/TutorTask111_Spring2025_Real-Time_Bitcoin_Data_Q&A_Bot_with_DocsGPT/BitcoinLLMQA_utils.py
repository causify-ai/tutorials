import requests 
import pandas as pd
from datetime import datetime
import numpy as np
from dotenv import load_dotenv
from llama_cpp import Llama
import matplotlib.pyplot as plt
from time import sleep
from random import uniform
import seaborn as sns
from scipy import stats
import os

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

load_dotenv()

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
CSV_FILENAME = 'bitcoin_prices.csv'

os.environ["LLAMA_CPP_LOG_LEVEL"] = "off" 

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

def add_log_returns(df):
    df['log_returns'] = np.log(df['price'] / df['price'].shift(1))
    return df

def compute_volatility(df, window=12):
    df = add_log_returns(df)
    df['volatility'] = df['log_returns'].rolling(window).std() * np.sqrt(window)
    return df

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
    
    df = compute_volatility(df)
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
    df.to_csv(CSV_FILENAME, index=False)
    print(f"Saved price: {new_price} | Volatility: {df['volatility'].iloc[-1]}")
    return df



def backfill_last_n_days_data(days, interval_minutes):
    """
    Backfill Bitcoin prices for the past `n` days at every `interval_minutes`
    using live data from the CoinGecko API.
    """
    now = datetime.now().replace(second=0, microsecond=0)
    intervals = int((days * 24 * 60) / interval_minutes)
    timestamps = [now - pd.Timedelta(minutes=i * interval_minutes) for i in range(intervals)][::-1]

    records = []
    for ts in timestamps:
        price = fetch_bitcoin_price()
        sleep(1.2)  # Respect API rate limit
        records.append({
            'timestamp': ts,
            'price': price, 
            'volatility': np.nan
        })

    df = pd.DataFrame(records)
    df = compute_volatility(df)
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df.to_csv(CSV_FILENAME, index=False)
    print(f"Backfilled {len(df)} rows of real-time API data into {CSV_FILENAME}")
    return df

# -----------------------------------------------------------------------------
# DcoGPT Setup
# -----------------------------------------------------------------------------

def setup_docsgpt():
    model_path = "llama-2-7b-chat.Q4_K_M.gguf"
    return Llama(
        model_path=model_path,
        n_ctx=2048,
        n_threads=6,
        n_gpu_layers=1
    )

def handle_query(llm, prompt):
    response = llm(
        prompt,
        max_tokens=200,
        stop=["\n", "###"],
        temperature=0.7
    )
    return response['choices'][0]['text'].strip()

def run_bitcoin_chatbot(llm, full_df):
    chat_history = ""
    context_summary = full_df.describe().to_string()

    print("Bitcoin Data Chatbot\n")

    while True:
        user_question = input("You: ").strip()
        if not user_question:
            print("Exiting the Bitcoin Q&A bot. Goodbye!")
            break

        # Build prompt with chat history and context
        chat_history += f"### User: {user_question}\n### Assistant:"
        full_prompt = (
            "You are a helpful assistant that answers questions about Bitcoin data.\n"
            f"(Context: {context_summary})\n"
            f"{chat_history}"
        )

        answer = handle_query(llm, full_prompt)
        print(f"\nYou: {user_question}\n")
        print(f"\nAssistant: {answer}\n")
        chat_history += f" {answer}\n"

# -----------------------------------------------------------------------------
# API Demonstration
# -----------------------------------------------------------------------------

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

# --------------------------------------------------
# Feature Engineering
# --------------------------------------------------
def add_technical_indicators(df):
    df = add_log_returns(df)
    df['MA_12'] = df['price'].rolling(12).mean()
    df['MA_24'] = df['price'].rolling(24).mean()
    df['Upper_BB'] = df['MA_24'] + 2 * df['price'].rolling(24).std()
    df['Lower_BB'] = df['MA_24'] - 2 * df['price'].rolling(24).std()
    df['High_Vol'] = df['volatility'] > df['volatility'].quantile(0.75)
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

def analyze_time_series(df):
    # Time-based aggregations
    hourly = df.resample('h').agg({
        'price': ['mean', 'max', 'min', 'std'],
        'volatility': 'mean'
    })
    
    daily = df.resample('D').agg({
        'price': ['mean', 'max', 'min', 'std'],
        'volatility': ['mean', 'max']
    })
    
    # Statistical properties
    price_stats = df['price'].describe()
    volatility_stats = df['volatility'].describe()
    
    # Correlation analysis
    corr_matrix = df[['price', 'volatility']].rolling(24).corr().unstack()['volatility']
    
    return {
        'hourly': hourly,
        'daily': daily,
        'price_stats': price_stats,
        'volatility_stats': volatility_stats,
        'correlation': corr_matrix
    }

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


def create_analysis_plots(df):
    plt.figure(figsize=(14, 10))
    
    # Price and Moving Averages
    plt.subplot(3, 1, 1)
    df['price'].plot(label='Price', alpha=0.5)
    df['MA_12'].plot(label='12-period MA')
    df['MA_24'].plot(label='24-period MA')
    plt.fill_between(df.index, df['Lower_BB'], df['Upper_BB'], alpha=0.1)
    plt.title('Price with Bollinger Bands')
    plt.legend()
    
    # Volatility Analysis
    plt.subplot(3, 1, 2)
    df['volatility'].plot(color='orange')
    plt.title('Rolling Volatility (1h window)')
    
    # Returns Distribution
    plt.subplot(3, 1, 3)
    sns.histplot(df['log_returns'].dropna(), kde=True, color='green')
    plt.title('Log Returns Distribution')
    
    plt.tight_layout()
    plt.show()

# --------------------------------------------------
# Statistical Summary
# --------------------------------------------------
def print_statistical_summary(df):
    print("Price Statistics:")
    print(df['price'].describe())
    
    print("\nVolatility Statistics:")
    print(df['volatility'].describe())
    
    print("\nCorrelation Matrix:")
    print(df[['price', 'volatility']].corr())
    
    # Normality tests
    print("\nNormality Tests:")
    print("Price Jarque-Bera:", stats.jarque_bera(df['price'].dropna()))
    print("Returns Shapiro:", stats.shapiro(df['log_returns'].dropna()))

# --------------------------------------------------
# Outlier Detection
# --------------------------------------------------
def detect_outliers(df):
    Q1 = df['price'].quantile(0.25)
    Q3 = df['price'].quantile(0.75)
    IQR = Q3 - Q1
    
    outliers = df[(df['price'] < (Q1 - 1.5 * IQR)) | 
                 (df['price'] > (Q3 + 1.5 * IQR))]
    
    return outliers

