import os
import pandas as pd
import psycopg2
from typing import Dict, List, Any, Union, Optional
import logging
import datetime

# Configure logging with better handling
def setup_logger(name, level=logging.INFO):
    """Set up a logger with proper formatting"""
    logger = logging.getLogger(name)
    
    # Only configure handlers if none exist
    if not logger.handlers:
        logger.setLevel(level)
        
        # Console handler
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Set propagate to False to avoid duplicate logging
        logger.propagate = False
    
    return logger

# Initialize logger
logger = setup_logger('sentiment_integration')

class SentimentIntegrator:
    """
    Class for integrating sentiment analysis data with Bitcoin price forecasting.
    
    Fetches sentiment data from the database and provides methods to incorporate
    it into the forecasting model.
    """
    
    def __init__(self):
        """
        Initialize the sentiment integrator.
        """
        # Initialize database connection
        self.db_url = os.environ.get('DATABASE_URL')
        if not self.db_url:
            logger.warning("DATABASE_URL environment variable not set, sentiment data will not be available")
    
    def get_sentiment_data(self, days: int = 30) -> pd.DataFrame:
        """
        Get sentiment data from the database.
        
        Args:
            days: Number of days to retrieve.
            
        Returns:
            DataFrame with sentiment data or empty DataFrame if not available.
        """
        if not self.db_url:
            return pd.DataFrame()
        
        conn = None
        try:
            conn = psycopg2.connect(self.db_url)
            
            query = f"""
                SELECT 
                    date, 
                    avg_polarity, 
                    avg_subjectivity, 
                    positive_count, 
                    negative_count, 
                    neutral_count, 
                    article_count
                FROM 
                    aggregate_sentiment
                WHERE 
                    date >= CURRENT_DATE - INTERVAL '{days} days'
                ORDER BY 
                    date ASC
            """
            
            df = pd.read_sql_query(query, conn)
            
            if df.empty:
                logger.warning("No sentiment data found in the database")
            else:
                logger.info(f"Retrieved {len(df)} days of sentiment data")
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting sentiment data: {str(e)}")
            return pd.DataFrame()
            
        finally:
            if conn:
                conn.close()
    
    def get_latest_sentiment(self) -> Dict[str, Any]:
        """
        Get the latest sentiment data.
        
        Returns:
            Dictionary with latest sentiment metrics or empty dict if not available.
        """
        sentiment_df = self.get_sentiment_data(days=7)
        
        if sentiment_df.empty:
            return {}
        
        # Get the most recent data
        latest = sentiment_df.iloc[-1]
        
        # Calculate sentiment trend (last 7 days)
        if len(sentiment_df) >= 3:
            sentiment_trend = sentiment_df['avg_polarity'].diff().mean()
        else:
            sentiment_trend = 0
        
        return {
            'date': latest['date'],
            'avg_polarity': latest['avg_polarity'],
            'avg_subjectivity': latest['avg_subjectivity'],
            'positive_count': latest['positive_count'],
            'negative_count': latest['negative_count'],
            'neutral_count': latest['neutral_count'],
            'article_count': latest['article_count'],
            'sentiment_trend': sentiment_trend
        }
    
    def create_sentiment_features(self, price_df: pd.DataFrame) -> pd.DataFrame:
        """
        Add sentiment features to price DataFrame.
        
        Args:
            price_df: DataFrame with price data.
            
        Returns:
            DataFrame with added sentiment features.
        """
        if not self.db_url:
            return price_df
        
        try:
            # Get sentiment data
            sentiment_df = self.get_sentiment_data(days=90)
            
            if sentiment_df.empty:
                return price_df
            
            # Convert date column to datetime
            sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
            sentiment_df = sentiment_df.set_index('date')
            
            # Ensure price_df has datetime index
            if not isinstance(price_df.index, pd.DatetimeIndex):
                logger.warning("Price DataFrame does not have DatetimeIndex, cannot merge sentiment data")
                return price_df
            
            # Resample sentiment data to match price data frequency
            price_freq = pd.infer_freq(price_df.index)
            if price_freq:
                sentiment_df = sentiment_df.resample(price_freq).mean().fillna(method='ffill')
            
            # Add sentiment features to price DataFrame
            result_df = price_df.copy()
            
            # Add sentiment polarity
            result_df['sentiment_polarity'] = None
            for date in result_df.index:
                date_str = date.strftime('%Y-%m-%d')
                if date_str in sentiment_df.index:
                    result_df.at[date, 'sentiment_polarity'] = sentiment_df.at[date_str, 'avg_polarity']
            
            # Fill missing values
            result_df['sentiment_polarity'] = result_df['sentiment_polarity'].fillna(method='ffill').fillna(0)
            
            # Create lagged features
            result_df['sentiment_polarity_lag1'] = result_df['sentiment_polarity'].shift(1)
            result_df['sentiment_polarity_lag2'] = result_df['sentiment_polarity'].shift(2)
            
            # Calculate momentum
            result_df['sentiment_momentum'] = result_df['sentiment_polarity'] - result_df['sentiment_polarity_lag1']
            
            # Fill NA values
            result_df = result_df.fillna(0)
            
            return result_df
            
        except Exception as e:
            logger.error(f"Error creating sentiment features: {str(e)}")
            return price_df
    
    def get_sentiment_summary(self) -> Dict[str, Any]:
        """
        Get a summary of sentiment data for display.
        
        Returns:
            Dictionary with sentiment summary.
        """
        latest = self.get_latest_sentiment()
        
        if not latest:
            return {
                'status': 'unavailable',
                'message': 'Sentiment data not available'
            }
        
        # Determine overall sentiment
        polarity = latest.get('avg_polarity', 0)
        if polarity > 0.1:
            sentiment = 'Positive'
            color = 'green'
        elif polarity < -0.1:
            sentiment = 'Negative'
            color = 'red'
        else:
            sentiment = 'Neutral'
            color = 'gray'
        
        # Format polarity for display
        polarity_display = f"{polarity:.2f}" if polarity is not None else "N/A"
        
        # Calculate sentiment distribution
        total_articles = latest.get('article_count', 0)
        if total_articles > 0:
            positive_pct = (latest.get('positive_count', 0) / total_articles) * 100
            negative_pct = (latest.get('negative_count', 0) / total_articles) * 100
            neutral_pct = (latest.get('neutral_count', 0) / total_articles) * 100
        else:
            positive_pct = negative_pct = neutral_pct = 0
        
        # Determine trend
        trend = latest.get('sentiment_trend', 0)
        if trend > 0.01:
            trend_text = 'Improving'
            trend_color = 'green'
        elif trend < -0.01:
            trend_text = 'Deteriorating'
            trend_color = 'red'
        else:
            trend_text = 'Stable'
            trend_color = 'gray'
        
        return {
            'status': 'available',
            'sentiment': sentiment,
            'color': color,
            'polarity': polarity_display,
            'date': latest.get('date', 'N/A'),
            'subjectivity': f"{latest.get('avg_subjectivity', 0):.2f}",
            'article_count': latest.get('article_count', 0),
            'positive_pct': f"{positive_pct:.1f}%",
            'negative_pct': f"{negative_pct:.1f}%",
            'neutral_pct': f"{neutral_pct:.1f}%",
            'trend': trend_text,
            'trend_color': trend_color
        }