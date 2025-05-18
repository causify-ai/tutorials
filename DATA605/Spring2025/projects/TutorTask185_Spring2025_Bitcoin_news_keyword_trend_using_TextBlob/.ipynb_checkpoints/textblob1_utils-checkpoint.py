"""
textblob1_utils.py
Reusable utility functions and API wrappers for Bitcoin News Keyword Trend Analysis.
"""

# =========================
# Imports
# =========================
import os
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import re
import time
from datetime import datetime
import nltk
from nltk.corpus import stopwords
from textblob import TextBlob
import string
from collections import Counter
import warnings
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import webbrowser
from statsmodels.tsa.stattools import grangercausalitytests, adfuller
from statsmodels.tools.sm_exceptions import MissingDataError

# Initialize NLTK resources
try:
    nltk.download('stopwords', quiet=True)
    nltk.download('punkt', quiet=True)
except:
    pass

# Enhanced stopword lists
EN_STOPWORDS = set(stopwords.words('english') if 'stopwords' in nltk.data.path else [])
MONTHS = set(['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'])
CRYPTO_COMMON_TERMS = set(['bitcoin', 'btc', 'cryptocurrency', 'crypto', 'blockchain'])

# Define custom stopwords as a flat list to avoid parsing issues
CUSTOM_STOPWORDS = {'\u2019', '\u2019s', 's', '\u2014', 'president', 'recent', 'said', 'mr', 'mrs', 'dr', 'etc', 'co',
                   'inc', 'ltd', 'corp', 'company', 'group', 'news', 'report', 'according', 'year',
                   'month', 'day', 'week', 'today', 'yesterday', 'tomorrow', 'article', 'writer',
                   'author', 'journalist', 'media', 'latest', 'update', 'breaking'}

# Check if running in Docker
def is_docker():
    """Check if running inside a Docker container"""
    path = '/proc/self/cgroup'
    return os.path.exists('/.dockerenv') or os.path.isfile(path) and any('docker' in line for line in open(path))

# =========================
# API Fetch Functions
# =========================
def fetch_bitcoin_news(api_key=None, days=30):
    """
    Fetch Bitcoin-related news articles from NewsAPI. Falls back to sample data if API key is not provided or fails.
    Args:
        api_key (str): NewsAPI key. If None, uses sample data.
        days (int): Number of days of news to fetch.
    Returns:
        pd.DataFrame: News articles with columns [title, description, publishedAt, source, date, hour]
    """
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    if api_key is None:
        # Use sample data
        sample_data = {
            'title': [
                'Bitcoin hits new high as institutional investors pile in',
                'Crypto regulations coming soon, says Treasury Secretary',
                'Bitcoin halving approaches, analysts predict price surge',
                'Market analysis shows crypto adoption increasing globally',
                'ETF approval speculation drives Bitcoin volatility'
            ],
            'description': [
                'Bitcoin price surges past $60,000 as major hedge funds announce investments',
                'New regulations expected by end of quarter, crypto exchanges preparing for compliance',
                'With the Bitcoin halving scheduled for April, analysts expect significant price movement',
                'Research shows cryptocurrency adoption has increased 40% year-over-year',
                'Market speculation about potential ETF approval has caused increased trading volume'
            ],
            'publishedAt': [
                '2023-05-01T08:00:00Z',
                '2023-05-02T10:30:00Z',
                '2023-05-03T12:15:00Z',
                '2023-05-04T14:45:00Z',
                '2023-05-05T09:20:00Z'
            ],
            'source': ['CryptoNews', 'FinanceDaily', 'InvestorPost', 'BlockchainReport', 'CryptoAnalyst']
        }
        news_df = pd.DataFrame(sample_data)
        news_df['publishedAt'] = pd.to_datetime(news_df['publishedAt'])
        news_df['date'] = news_df['publishedAt'].dt.date
        news_df['hour'] = news_df['publishedAt'].dt.hour
        
        # Save sample data
        news_df.to_csv('data/bitcoin_news.csv', index=False)
        return news_df
    else:
        # Fetch from NewsAPI
        url = 'https://newsapi.org/v2/everything'
        params = {
            'q': 'bitcoin',
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 100,
            'apiKey': api_key,
        }
        all_articles = []
        for page in range(1, min(days, 5) + 1):
            params['page'] = page
            resp = requests.get(url, params=params)
            if resp.status_code != 200:
                break
            data = resp.json()
            for article in data.get('articles', []):
                all_articles.append({
                    'title': article['title'],
                    'description': article['description'],
                    'publishedAt': article['publishedAt'],
                    'source': article['source']['name']
                })
        news_df = pd.DataFrame(all_articles)
        if not news_df.empty:
            news_df['publishedAt'] = pd.to_datetime(news_df['publishedAt'])
            news_df['date'] = news_df['publishedAt'].dt.date
            news_df['hour'] = news_df['publishedAt'].dt.hour
            
            # Save to CSV
            news_df.to_csv('data/bitcoin_news.csv', index=False)
        return news_df

def fetch_bitcoin_prices(days=30, interval='daily'):
    """
    Fetch historical Bitcoin price data from CoinGecko API.
    Falls back to sample data if API is unavailable.
    
    Args:
        days (int): Number of days of price data.
        interval (str): 'daily' or 'hourly'.
    Returns:
        pd.DataFrame: Price data with columns [timestamp, price, date, hour]
    """
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    try:
        # Use CoinGecko API for real data
        if days > 90 and interval == 'hourly':
            # CoinGecko limits hourly data to 90 days
            days = 90
            print(f"Limiting hourly data request to {days} days (API limitation)")
        
        # Build API URL based on interval
        if interval == 'daily':
            url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={days}&interval=daily"
        else:
            url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days={days}"
        
        print(f"Fetching Bitcoin price data for the past {days} days...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Process the price data
            prices = data.get('prices', [])
            if prices:
                # Convert to DataFrame
                df = pd.DataFrame(prices, columns=['timestamp_ms', 'price'])
                
                # Convert timestamp from milliseconds to datetime
                df['timestamp'] = pd.to_datetime(df['timestamp_ms'], unit='ms')
                df['date'] = df['timestamp'].dt.date
                df['hour'] = df['timestamp'].dt.hour
                
                # Clean up
                df = df[['timestamp', 'price', 'date', 'hour']]
                
                # Save to CSV
                df.to_csv('data/bitcoin_prices.csv', index=False)
                print(f"Successfully fetched {len(df)} Bitcoin price data points")
                return df
        
        print("API request failed or returned no data. Using sample data instead.")
    except Exception as e:
        print(f"Error fetching price data: {str(e)}. Using sample data instead.")
    
    # If we reach here, API call failed - use sample data
    print("Generating sample Bitcoin price data...")
    end_date = datetime.now()
    start_date = end_date - pd.Timedelta(days=days)
    dates = pd.date_range(start=start_date, periods=days)
    
    # More realistic Bitcoin price simulation
    base_price = 65000  # More current base price
    volatility = 0.02  # 2% daily volatility
    
    prices = [base_price]
    for i in range(1, days):
        # Random walk with slight upward bias
        change = prices[-1] * (1 + np.random.normal(0.001, volatility))
        prices.append(change)
    
    price_df = pd.DataFrame({
        'timestamp': dates,
        'price': prices,
        'date': dates.date,
        'hour': [0]*days
    })
    
    # Save to CSV
    price_df.to_csv('data/bitcoin_prices.csv', index=False)
    print("Sample price data created")
    return price_df

def fetch_current_bitcoin_price():
    """
    Fetch the current Bitcoin price from CoinGecko API.
    Returns a real-time value or falls back to a simulated price if retrieval fails.
    
    Returns:
        dict: {'price': current price, 'timestamp': datetime}
    """
    try:
        # Use CoinGecko API for real-time price
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_last_updated_at=true"
        print("Fetching current Bitcoin price from CoinGecko...")
        
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'bitcoin' in data:
                price = data['bitcoin']['usd']
                
                # Get timestamp or use current time
                timestamp = datetime.now()
                if 'last_updated_at' in data['bitcoin']:
                    timestamp = datetime.fromtimestamp(data['bitcoin']['last_updated_at'])
                
                print(f"Current Bitcoin price: ${price:,.2f}")
                return {
                    'price': price,
                    'timestamp': timestamp
                }
        
        print("API request failed. Using simulated price instead.")
    except Exception as e:
        print(f"Error fetching current Bitcoin price: {str(e)}. Using simulated price instead.")
    
    # If API call failed, use simulated price
    current_price = 65000 + np.random.normal(0, 1000)  # More current price baseline
    return {
        'price': current_price,
        'timestamp': datetime.now()
    }

# =========================
# Data Processing Functions
# =========================
def is_good_keyword(kw):
    """
    Determine if a keyword is valuable for analysis.
    
    Args:
        kw (str): The keyword to evaluate
        
    Returns:
        bool: True if the keyword is valuable, False otherwise
    """
    kw = kw.lower().strip()
    
    # Basic filtering
    if len(kw) <= 2:
        return False
    if kw in EN_STOPWORDS:
        return False
    if kw in MONTHS:
        return False
    if kw in CUSTOM_STOPWORDS:
        return False
    if kw.isnumeric():
        return False
    if any(char.isdigit() for char in kw):
        return False
    if all(char in string.punctuation for char in kw):
        return False
    if sum(c.isalpha() for c in kw) < 2:
        return False
        
    return True

def extract_important_keywords(text, is_title=False):
    """
    Extract and weight keywords more intelligently.
    
    Args:
        text (str): The text to extract keywords from
        is_title (bool): Whether the text is a title (gives higher weight)
        
    Returns:
        list: List of extracted keywords
    """
    if not text or not isinstance(text, str):
        return []
        
    blob = TextBlob(text)
    keywords = [phrase.lower() for phrase in blob.noun_phrases]
    
    # Add individual nouns that might be important but not caught as phrases
    for word, tag in blob.tags:
        if tag.startswith('NN') and is_good_keyword(word):
            keywords.append(word.lower())
    
    # Filter keywords
    keywords = [kw for kw in keywords if is_good_keyword(kw)]
    
    # Add specific cryptocurrency-related terms that might be in CRYPTO_COMMON_TERMS
    # but are still important to track
    crypto_specific = ['halving', 'etf', 'regulation', 'adoption', 'institutional', 
                       'volatility', 'bull', 'bear', 'rally', 'crash']
    for term in crypto_specific:
        if term in text.lower() and term not in keywords:
            keywords.append(term)
    
    return keywords

def extract_keywords(news_df=None, min_frequency=1, include_titles=True):
    """
    Extract keywords from news articles using TextBlob. Returns DataFrame with keywords per article.
    Args:
        news_df (pd.DataFrame): DataFrame of news articles. If None, tries to load from data/bitcoin_news.csv.
        min_frequency (int): Minimum frequency for a keyword to be included.
        include_titles (bool): Whether to include titles in keyword extraction.
    Returns:
        pd.DataFrame: News with keywords column (list of keywords)
    """
    try:
        # If no DataFrame provided, try to load from file
        if news_df is None:
            if not os.path.exists('data/bitcoin_news.csv'):
                print("No news data found. Please fetch news articles first.")
                return None
            news_df = pd.read_csv('data/bitcoin_news.csv')
            
        # Process each article
        all_keywords = []
        article_keywords = []
        
        for i, row in news_df.iterrows():
            # Extract from title (with higher weight)
            title_keywords = []
            if include_titles and isinstance(row.get('title'), str):
                title_keywords = extract_important_keywords(row['title'], is_title=True)
                # Add title keywords twice to give them higher weight
                all_keywords.extend(title_keywords)
                all_keywords.extend(title_keywords)  # Duplicated for higher weight
            
            # Extract from description
            desc_keywords = []
            if isinstance(row.get('description'), str):
                desc_keywords = extract_important_keywords(row['description'])
                all_keywords.extend(desc_keywords)
            
            # Combine keywords for this article
            combined_keywords = list(set(title_keywords + desc_keywords))
            article_keywords.append(combined_keywords)
            
        # Add keywords to each article
        news_df = news_df.copy()
        news_df['keywords'] = article_keywords
        
        # Count keyword frequencies
        keyword_counts = Counter(all_keywords)
        
        # Filter by minimum frequency
        filtered_keywords = {k: v for k, v in keyword_counts.items() if v >= min_frequency}
        
        # Create DataFrame with keyword frequencies
        keywords_df = pd.DataFrame({
            'keyword': list(filtered_keywords.keys()),
            'frequency': list(filtered_keywords.values())
        })
        
        # Sort by frequency
        keywords_df = keywords_df.sort_values('frequency', ascending=False)
        
        # Save results
        os.makedirs('data', exist_ok=True)
        news_df.to_csv('data/bitcoin_news_with_keywords.csv', index=False)
        keywords_df.to_csv('data/keyword_frequencies.csv', index=False)
        
        return news_df
        
    except Exception as e:
        print(f"Error extracting keywords: {str(e)}")
        return None

def analyze_trends(news_with_keywords=None, price_df=None, time_window='daily', min_freq=1):
    """
    Analyze keyword trends and merge with price data.
    Args:
        news_with_keywords (pd.DataFrame): News with keywords column. If None, tries to load from data file.
        price_df (pd.DataFrame): Bitcoin price data. If None, tries to load from data file.
        time_window (str): 'daily' or 'hourly'.
        min_freq (int): Minimum frequency for a keyword to be included.
    Returns:
        pd.DataFrame: Trends with columns [keyword, time_window, count, price, frequency, correlation]
    """
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # If no news data provided, try to load from file
    if news_with_keywords is None:
        if os.path.exists('data/bitcoin_news_with_keywords.csv'):
            news_with_keywords = pd.read_csv('data/bitcoin_news_with_keywords.csv')
        else:
            print("No news data with keywords found. Please extract keywords first.")
            return None
    
    # If no price data provided, try to load from file
    if price_df is None:
        if os.path.exists('data/bitcoin_prices.csv'):
            price_df = pd.read_csv('data/bitcoin_prices.csv')
        else:
            print("No price data found. Please fetch price data first.")
            return None
    
    # Count keyword frequency per time window
    records = []
    for idx, row in news_with_keywords.iterrows():
        # Convert string representation of lists to actual lists if needed
        kws = row['keywords']
        if isinstance(kws, str):
            try:
                # Handle string representation of lists from CSV
                kws = eval(kws)
            except:
                kws = []
        
        date = row['date']
        # Convert string to datetime.date if needed
        if isinstance(date, str):
            date = pd.to_datetime(date).date()
        
        for kw in kws:
            records.append({'keyword': kw, 'date': date})
    
    kw_df = pd.DataFrame(records)
    
    # Skip further processing if no keywords found
    if kw_df.empty:
        print("No keywords found for analysis.")
        return None
    
    if time_window == 'daily':
        group = kw_df.groupby(['keyword', 'date']).size().reset_index(name='count')
        group = group.rename(columns={'date': 'time_window'})
    else:
        # For hourly, you could add hour granularity
        group = kw_df.groupby(['keyword', 'date']).size().reset_index(name='count')
        group = group.rename(columns={'date': 'time_window'})
    
    # Convert price dataframe date column to datetime.date if needed
    if 'date' in price_df.columns and not isinstance(price_df['date'].iloc[0], pd.Timestamp):
        if isinstance(price_df['date'].iloc[0], str):
            price_df['date'] = pd.to_datetime(price_df['date']).dt.date
    
    # Merge with price
    merged = group.merge(price_df[['date', 'price']], left_on='time_window', right_on='date', how='left')
    merged = merged.drop(columns=['date'])
    
    # Calculate frequency and correlation
    freq = merged.groupby('keyword')['count'].sum().reset_index(name='frequency')
    merged = merged.merge(freq, on='keyword')
    
    # Filter by minimum frequency if specified
    if min_freq > 1:
        merged = merged[merged['frequency'] >= min_freq]
    
    # Calculate correlation for each keyword
    merged['correlation'] = merged.groupby('keyword').apply(
        lambda g: g['count'].corr(g['price']) if len(g) > 1 else np.nan
    ).reset_index(level=0, drop=True)
    
    # Save the merged data
    merged.to_csv('data/merged_keyword_price.csv', index=False)
    return merged

# =========================
# Visualization Functions
# =========================
def plot_keyword_vs_price(merged_df, keyword, save_fig=False, display_fig=True):
    """
    Plot keyword frequency vs Bitcoin price for a given keyword.
    Args:
        merged_df (pd.DataFrame): DataFrame from analyze_trends.
        keyword (str): Keyword to plot.
        save_fig (bool): Whether to save the figure.
        display_fig (bool): Whether to display the figure.
    """
    data = merged_df[merged_df['keyword'] == keyword]
    if data.empty:
        print(f"No data for keyword '{keyword}'")
        return
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax2 = ax1.twinx()
    ax1.plot(data['time_window'], data['count'], color='tab:blue', marker='o', label='Keyword Frequency')
    ax2.plot(data['time_window'], data['price'], color='tab:orange', marker='s', label='Bitcoin Price')
    ax1.set_xlabel('Date')
    ax1.set_ylabel(f"'{keyword}' Frequency", color='tab:blue')
    ax2.set_ylabel('Bitcoin Price (USD)', color='tab:orange')
    plt.title(f"'{keyword}' Frequency vs Bitcoin Price")
    fig.tight_layout()
    if save_fig:
        os.makedirs('figures', exist_ok=True)
        plt.savefig(f'figures/{keyword}_vs_price.png', dpi=300, bbox_inches='tight')
    if display_fig:
        plt.show()
    else:
        plt.close()

def plot_keyword_price_heatmap(merged_df=None, top_n=10, save_fig=False, display_fig=True):
    """
    Plot a heatmap of keyword-price correlations for top N keywords.
    Args:
        merged_df (pd.DataFrame): DataFrame from analyze_trends. If None, tries to load from data file.
        top_n (int): Number of top keywords to show.
        save_fig (bool): Whether to save the figure.
        display_fig (bool): Whether to display the figure.
    """
    # If no data provided, try to load from file
    if merged_df is None:
        if os.path.exists('data/merged_keyword_price.csv'):
            merged_df = pd.read_csv('data/merged_keyword_price.csv')
        else:
            print("No merged data found. Please run analyze_trends() first.")
            return
    
    # Get top N keywords by frequency
    top_keywords = merged_df.groupby('keyword')['frequency'].max().nlargest(top_n).index.tolist()
    corr_data = merged_df[merged_df['keyword'].isin(top_keywords)][['keyword', 'correlation']].drop_duplicates()
    corr_matrix = corr_data.set_index('keyword')['correlation']
    plt.figure(figsize=(8, max(4, len(top_keywords) * 0.5)))
    sns.heatmap(corr_matrix.values.reshape(-1, 1), annot=True, yticklabels=corr_matrix.index, xticklabels=['Correlation'], cmap='coolwarm', center=0)
    plt.title('Keyword-Price Correlations')
    plt.ylabel('Keyword')
    plt.tight_layout()
    if save_fig:
        os.makedirs('figures', exist_ok=True)
        plt.savefig('figures/keyword_price_correlation.png', dpi=300, bbox_inches='tight')
    if display_fig:
        plt.show()
    else:
        plt.close()

# =========================
# Granger Causality Testing
# =========================
def run_stationarity_test(series):
    """
    Test if a time series is stationary using the Augmented Dickey-Fuller test.
    
    Args:
        series (array-like): The time series to test
        
    Returns:
        tuple: (is_stationary, p_value)
    """
    # Handle special cases
    if len(series) < 5:  # Need enough data points
        return False, 1.0
    if len(np.unique(series)) < 2:  # Constant series
        return False, 1.0
        
    try:
        # Run ADF test
        result = adfuller(series, autolag='AIC')
        p_value = result[1]
        return p_value < 0.05, p_value
    except Exception as e:
        print(f"Error in stationarity test: {str(e)}")
        return False, 1.0

def make_stationary(series):
    """
    Transform a series to make it stationary.
    First tries differencing, then differencing of logs if needed.
    
    Args:
        series (array-like): The time series to transform
        
    Returns:
        array: The stationary series, or the original if transformation failed
    """
    # Check if already stationary
    is_stationary, _ = run_stationarity_test(series)
    if is_stationary:
        return series
        
    # Try first differencing
    diff = np.diff(series)
    is_stationary, _ = run_stationarity_test(diff)
    if is_stationary:
        return diff
        
    # Try log transform + differencing for non-negative series
    if np.all(series > 0):
        try:
            log_diff = np.diff(np.log(series))
            is_stationary, _ = run_stationarity_test(log_diff)
            if is_stationary:
                return log_diff
        except Exception:
            pass
            
    # Return original differenced series as fallback
    return diff

def run_granger_tests(merged_df=None, top_n=10, max_lag=3, min_data_points=10):
    """
    Perform Granger causality tests between keyword frequencies and price changes.
    
    Args:
        merged_df (pd.DataFrame): DataFrame from analyze_trends. If None, tries to load from file.
        top_n (int): Number of top keywords to analyze
        max_lag (int): Maximum lag to test for causality
        min_data_points (int): Minimum number of data points required for testing
        
    Returns:
        pd.DataFrame: Results of Granger causality tests
    """
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    try:
        # If no data provided, try to load from file
        if merged_df is None:
            if os.path.exists('data/merged_keyword_price.csv'):
                merged_df = pd.read_csv('data/merged_keyword_price.csv')
            else:
                print("No merged data found. Please run analyze_trends() first.")
                return None
        
        # Convert date column if needed
        if 'time_window' in merged_df.columns and not pd.api.types.is_datetime64_dtype(merged_df['time_window']):
            merged_df['time_window'] = pd.to_datetime(merged_df['time_window'])
        
        # Get top N keywords by frequency
        keyword_counts = merged_df['keyword'].value_counts()
        top_keywords = keyword_counts.nlargest(top_n).index.tolist()
        
        # Store results
        results = []
        
        # Process each keyword
        for keyword in top_keywords:
            # Filter data for this keyword
            keyword_data = merged_df[merged_df['keyword'] == keyword].sort_values('time_window')
            
            # Skip if not enough data points
            if len(keyword_data) < min_data_points:
                print(f"Skipping '{keyword}': only {len(keyword_data)} data points (need {min_data_points})")
                continue
                
            # Prepare time series
            keyword_series = keyword_data['count'].values
            price_series = keyword_data['price'].values
            
            # Check stationarity
            kw_stationary, kw_p = run_stationarity_test(keyword_series)
            price_stationary, price_p = run_stationarity_test(price_series)
            
            if not kw_stationary:
                keyword_series = make_stationary(keyword_series)
                
            if not price_stationary:
                price_series = make_stationary(price_series)
            
            # Make sure we still have enough data after transformations
            if len(keyword_series) < min_data_points or len(price_series) < min_data_points:
                print(f"Skipping '{keyword}': insufficient data after transformations")
                continue
                
            # Create DataFrame for Granger test with equal length series
            min_len = min(len(keyword_series), len(price_series))
            test_data = pd.DataFrame({
                'keyword': keyword_series[:min_len],
                'price': price_series[:min_len]
            })
            
            # Calculate correlation
            correlation = test_data['keyword'].corr(test_data['price'])
            
            # Determine max lag to use (min of specified max_lag and 1/3 of data points)
            actual_max_lag = min(max_lag, len(test_data)//3)
            if actual_max_lag < 1:
                actual_max_lag = 1
            
            # Perform Granger causality tests
            try:
                # Test if keywords Granger-cause price changes
                keyword_to_price = grangercausalitytests(
                    test_data[['price', 'keyword']],
                    maxlag=actual_max_lag,
                    verbose=False
                )
                
                # Test if price changes Granger-cause keywords
                price_to_keyword = grangercausalitytests(
                    test_data[['keyword', 'price']],
                    maxlag=actual_max_lag,
                    verbose=False
                )
                
                # Get best lag results
                best_lag_k2p = max(
                    range(1, actual_max_lag + 1),
                    key=lambda x: 1 - keyword_to_price[x][0]['ssr_chi2test'][1]
                )
                
                best_lag_p2k = max(
                    range(1, actual_max_lag + 1),
                    key=lambda x: 1 - price_to_keyword[x][0]['ssr_chi2test'][1]
                )
                
                # Get p-values for best lags
                k2p_pvalue = keyword_to_price[best_lag_k2p][0]['ssr_chi2test'][1]
                p2k_pvalue = price_to_keyword[best_lag_p2k][0]['ssr_chi2test'][1]
                
                # Add results
                results.append({
                    'keyword': keyword,
                    'data_points': len(test_data),
                    'correlation': correlation,
                    'best_lag_k2p': best_lag_k2p,
                    'best_lag_p2k': best_lag_p2k,
                    'k2p_pvalue': k2p_pvalue,
                    'p2k_pvalue': p2k_pvalue,
                    'k2p_significant': k2p_pvalue < 0.05,
                    'p2k_significant': p2k_pvalue < 0.05
                })
                
            except Exception as e:
                print(f"Error testing '{keyword}': {str(e)}")
                continue
        
        if not results:
            print("No valid Granger causality tests could be performed")
            return None
            
        # Create results DataFrame
        results_df = pd.DataFrame(results)
        
        # Save results
        results_df.to_csv('data/granger_causality_results.csv', index=False)
        
        return results_df
        
    except Exception as e:
        print(f"Error in Granger causality testing: {str(e)}")
        return None

# =========================
# Dashboard Generation
# =========================
def generate_dashboard(merged_df=None, output_path='dashboard/index.html'):
    """
    Generate a comprehensive HTML dashboard summarizing the analysis.
    Args:
        merged_df (pd.DataFrame): DataFrame from analyze_trends. If None, tries to load from data file.
        output_path (str): Path to save the dashboard HTML.
    Returns:
        str: Path to the generated dashboard.
    """
    # Create necessary directories
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Current time for dashboard timestamp
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # If no data provided, try to load from file
    if merged_df is None:
        if os.path.exists('data/merged_keyword_price.csv'):
            merged_df = pd.read_csv('data/merged_keyword_price.csv')
        else:
            print("No merged data found. Please run analyze_trends() first.")
            return None
    
    # Check for Granger causality results
    granger_results = None
    if os.path.exists('data/granger_causality_results.csv'):
        granger_results = pd.read_csv('data/granger_causality_results.csv')
    
    # Get current Bitcoin price if available
    current_price = fetch_current_bitcoin_price()
    price_display = f"${current_price['price']:,.2f}" if current_price else "Not available"
    
    # Get top keywords
    top_keywords = merged_df.groupby('keyword')['frequency'].max().nlargest(5).index.tolist()
    
    # Build HTML for dashboard
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bitcoin News Keyword Analysis Dashboard</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
                background-color: #f5f5f5;
            }}
            header {{
                background-color: #1a1a1a;
                color: #f2a900;
                padding: 1rem;
                text-align: center;
            }}
            .current-price {{
                background-color: #f2a900;
                color: #1a1a1a;
                padding: 0.5rem 1rem;
                border-radius: 5px;
                font-weight: bold;
                display: inline-block;
                margin-top: 0.5rem;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #fff;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }}
            .dashboard-timestamp {{
                text-align: right;
                color: #777;
                font-size: 0.8rem;
                margin-bottom: 20px;
            }}
            h1, h2, h3 {{
                color: #333;
            }}
            .card {{
                background-color: white;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                padding: 20px;
                margin-bottom: 20px;
            }}
            .keyword-chip {{
                display: inline-block;
                background-color: #e0e0e0;
                padding: 5px 15px;
                margin: 5px;
                border-radius: 20px;
                font-size: 0.9rem;
            }}
            .keyword-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            .keyword-table th, .keyword-table td {{
                border: 1px solid #ddd;
                padding: 8px;
            }}
            .keyword-table th {{
                background-color: #f2f2f2;
                text-align: left;
            }}
            .keyword-table tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            .keyword-table tr:hover {{
                background-color: #f1f1f1;
            }}
        </style>
    </head>
    <body>
        <header>
            <h1>🔎 Bitcoin News Keyword Analysis Dashboard 🔎</h1>
            <div class="current-price">Current BTC Price: {price_display}</div>
        </header>
        
        <div class="container">
            <div class="dashboard-timestamp">
                Generated: {current_time}
            </div>
            
            <div class="card">
                <h2>Analysis Overview</h2>
                <p>This dashboard visualizes the correlation between Bitcoin news keyword frequency and price movements.</p>
                
                <h3>Top Keywords</h3>
                <div>
                    {''.join([f'<span class="keyword-chip">{kw}</span>' for kw in top_keywords])}
                </div>
            </div>
            
            <div class="card">
                <h2>Keyword Frequency Summary</h2>
                <table class="keyword-table">
                    <tr>
                        <th>Keyword</th>
                        <th>Frequency</th>
                        <th>Correlation with Price</th>
                    </tr>
    """
    
    # Add rows for top keywords
    for keyword in top_keywords:
        # Get frequency and correlation for this keyword
        keyword_data = merged_df[merged_df['keyword'] == keyword]
        if not keyword_data.empty:
            freq = keyword_data['frequency'].max()
            corr = keyword_data['correlation'].iloc[0]
            html += f"""
                    <tr>
                        <td>{keyword}</td>
                        <td>{freq}</td>
                        <td>{corr:.3f}</td>
                    </tr>
            """
    
    html += """
                </table>
            </div>
    """
    
    # Add Granger causality section if available
    if granger_results is not None and not granger_results.empty:
        html += """
            <div class="card">
                <h2>Granger Causality Test Results</h2>
                <p>Tests whether keywords can predict price changes, or vice versa.</p>
                <table class="keyword-table">
                    <tr>
                        <th>Keyword</th>
                        <th>Correlation</th>
                        <th>Keyword → Price (p-value)</th>
                        <th>Price → Keyword (p-value)</th>
                    </tr>
        """
        
        # Sort by p-value (ascending)
        granger_results_sorted = granger_results.sort_values('k2p_pvalue')
        
        for _, row in granger_results_sorted.head(10).iterrows():
            keyword = row['keyword']
            corr = row['correlation']
            k2p = row['k2p_pvalue']
            p2k = row['p2k_pvalue']
            k2p_significant = "✓" if row['k2p_significant'] else "✗"
            p2k_significant = "✓" if row['p2k_significant'] else "✗"
            
            html += f"""
                    <tr>
                        <td>{keyword}</td>
                        <td>{corr:.3f}</td>
                        <td>{k2p_significant} ({k2p:.4f})</td>
                        <td>{p2k_significant} ({p2k:.4f})</td>
                    </tr>
            """
        
        html += """
                </table>
            </div>
        """
    
    # Close HTML
    html += """
            <div class="card">
                <h2>Visualization</h2>
                <p>See the <code>figures/</code> directory for detailed visualizations of keyword trends and price correlations.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Write HTML to file
    with open(output_path, 'w') as f:
        f.write(html)
    
    print(f"Dashboard generated at: {output_path}")
    return output_path 