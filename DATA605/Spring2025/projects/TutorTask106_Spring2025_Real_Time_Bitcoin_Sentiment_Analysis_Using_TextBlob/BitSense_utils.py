"""
template_utils.py

This file contains utility functions that support the tutorial notebooks.

- Notebooks should call these functions instead of writing raw logic inline.
- This helps keep the notebooks clean, modular, and easier to debug.
- Students should implement functions here for data preprocessing,
  model setup, evaluation, or any reusable logic.
"""

import pandas as pd
import numpy as np
import logging
from sklearn.model_selection import train_test_split
# from pycaret.classification import compare_models
from dotenv import load_dotenv
from src.logger import get_logger
from src.common import newsapi, coingecko, RELEVANT_SOURCES
from datetime import datetime, timedelta
import time
from textblob import TextBlob
# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
load_dotenv()

# Set up logging
logger = get_logger(__name__)
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


def fetch_bitcoin_news(start_date, end_date, refresh=False):
    """
    Fetch Bitcoin-related news articles from NewsAPI.

    Args:
        start_date (str): Start date in 'YYYY-MM-DD' format
        end_date (str): End date in 'YYYY-MM-DD' format
        refresh (bool): Ignored, included for interface compatibility

    Returns:
        pandas.DataFrame: DataFrame containing news articles
    """
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')

    today = datetime.now().date()
    earliest_allowed = today - timedelta(days=29)
    if start_dt.date() < earliest_allowed:
        msg = f"Adjusting start date from {start_dt.date()} to {earliest_allowed} due to NewsAPI's 30-day limit"
        logger.warning(msg)
        start_dt = datetime.combine(earliest_allowed, datetime.min.time())

    if not newsapi:
        logger.error("NewsAPI key not available. Please set the NEWS_API_KEY environment variable.")
        return None

    articles = []
    try:
        try:
            key_status = newsapi.get_sources()
            if key_status.get('status') == 'ok':
                logger.info("Using valid NewsAPI key")
        except:
            logger.warning("Unable to verify NewsAPI key")

        current_date = start_dt
        total_articles = 0

        # Break into 1-day chunks to avoid 100 article cap
        while current_date <= end_dt:
            next_date = min(current_date + timedelta(days=1), end_dt)
            from_date = current_date.strftime('%Y-%m-%d')
            to_date = next_date.strftime('%Y-%m-%d')
            sources_param = ','.join(RELEVANT_SOURCES)
            
            try:
                response = newsapi.get_everything(
                    q='bitcoin OR crypto OR cryptocurrency',
                    language='en',
                    sources=sources_param,  # <-- NEW: filter by trusted sources
                    from_param=from_date,
                    to=to_date,
                    sort_by='publishedAt',
                    page=1,  # Only page 1 to avoid hitting free-tier limit
                    page_size=100
                )

                if response.get('articles'):
                    batch_articles = [{
                        'title': a.get('title', ''),
                        'description': a.get('description', ''),
                        'content': a.get('content', ''),
                        'source': a.get('source', {}).get('name', 'Unknown'),
                        'author': a.get('author', 'Unknown'),
                        'url': a.get('url', ''),
                        'publishedAt': a.get('publishedAt', '')
                    } for a in response['articles']]

                    articles.extend(batch_articles)
                    total_articles += len(batch_articles)

                    if len(batch_articles) == 100:
                        logger.warning(f"Hit 100-article cap for {from_date}. More articles likely exist but are not retrievable with free tier.")

                time.sleep(0.5)
            except Exception as e:
                logger.warning(f"Error fetching news for {from_date} to {to_date}: {str(e)}")

            current_date = next_date + timedelta(days=1)
            time.sleep(0.5)

        if articles:
            df = pd.DataFrame(articles)
            df['publishedAt'] = pd.to_datetime(df['publishedAt'], errors='coerce')
            df['date'] = df['publishedAt'].dt.date
            filtered_df = df[(df['date'] >= start_dt.date()) & (df['date'] <= end_dt.date())]
            logger.info(f"Retrieved {len(filtered_df)} articles from NewsAPI for {start_date} to {end_date}")
            return filtered_df
        else:
            logger.warning("No articles found for the specified date range.")
            return None

    except Exception as e:
        logger.error(f"Error fetching news: {str(e)}")
        return None

def fetch_bitcoin_prices(start_date, end_date, refresh=False):
    """
    Fetch Bitcoin historical price data from CoinGecko API.
    
    Args:
        start_date (str): Start date in 'YYYY-MM-DD' format
        end_date (str): End date in 'YYYY-MM-DD' format
        refresh (bool): Currently unused; all data is fetched fresh from API
    
    Returns:
        pandas.DataFrame: DataFrame containing price data
    """
    try:
        # Convert date strings to datetime objects
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Convert date strings to unix timestamps (required by CoinGecko)
        start_timestamp = int(start_dt.timestamp())
        end_timestamp = int(end_dt.timestamp()) + 86400  # Add one day to include end_date
        
        msg = "Fetching Bitcoin price data from CoinGecko API..."
        logger.info(msg)
        logger.info(msg)
        
        # Fetch data
        market_data = coingecko.get_coin_market_chart_range_by_id(
            id='bitcoin',
            vs_currency='usd',
            from_timestamp=start_timestamp,
            to_timestamp=end_timestamp
        )
        
        prices_data = market_data.get('prices', [])
        
        if prices_data:
            # Convert to DataFrame
            df = pd.DataFrame(prices_data, columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['date'] = df['timestamp'].dt.date
            
            # Aggregate by date
            daily_prices = df.groupby('date').agg(
                open_price=('price', 'first'),
                close_price=('price', 'last'),
                high_price=('price', 'max'),
                low_price=('price', 'min'),
                avg_price=('price', 'mean')
            ).reset_index()
            
            # Add percentage change
            daily_prices['price_change_pct'] = daily_prices['close_price'].pct_change() * 100
            
            logger.info(f"Retrieved Bitcoin price data for {len(daily_prices)} days.")
            logger.info(f"Retrieved Bitcoin price data for {len(daily_prices)} days.")
            return daily_prices
        else:
            msg = "No price data found for the specified date range."
            logger.warning(msg)
            logger.warning(msg)
            return None

    except Exception as e:
        error_msg = f"Error fetching Bitcoin prices: {str(e)}"
        logger.error(error_msg)
        logger.error(error_msg)
        return None
        
def analyze_sentiment(articles_df):
    """
    Analyze sentiment of news articles using TextBlob.

    Args:
        articles_df (pandas.DataFrame): DataFrame containing news articles.

    Returns:
        pandas.DataFrame: DataFrame with added sentiment scores and categories.
    """
    if articles_df is None or articles_df.empty:
        logger.warning("No articles to analyze.")
        return None

    logger.info("Analyzing sentiment of news articles...")

    df = articles_df.copy()
    df['polarity'] = np.nan
    df['subjectivity'] = np.nan

    def get_sentiment(text):
        if not isinstance(text, str) or not text.strip():
            return 0.0, 0.0
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity, blob.sentiment.subjectivity
        except Exception as e:
            logger.warning(f"Error analyzing sentiment: {e}")
            return 0.0, 0.0

    # Apply sentiment analysis
    for idx, row in df.iterrows():
        text = row.get('content') or row.get('description') or row.get('title')
        polarity, subjectivity = get_sentiment(text)
        df.at[idx, 'polarity'] = polarity
        df.at[idx, 'subjectivity'] = subjectivity

    # Classify sentiment category
    df['sentiment_category'] = pd.cut(
        df['polarity'],
        bins=[-1.1, -0.5, -0.1, 0.1, 0.5, 1.1],
        labels=['Very Negative', 'Negative', 'Neutral', 'Positive', 'Very Positive']
    )

    logger.info(f"Sentiment analysis completed for {len(df)} articles.")
    return df