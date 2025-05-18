import os
import json
import time
import datetime
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from newsapi import NewsApiClient
from textblob import TextBlob
from typing import Dict, List, Any, Union, Optional

# Import logging configuration
try:
    from logging_config import setup_logging
    logger = setup_logging('sentiment_analyzer')
except ImportError:
    # Fallback if logging_config.py is not available
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('sentiment_analyzer')

class BitcoinSentimentAnalyzer:
    """
    Class for analyzing sentiment of Bitcoin-related news articles.
    
    Fetches news using NewsAPI, analyzes sentiment using TextBlob,
    and stores results in PostgreSQL database.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the sentiment analyzer.
        
        Args:
            api_key: NewsAPI key. If None, uses environment variable.
        """
        # Initialize NewsAPI client
        self.api_key = api_key or os.environ.get('NEWS_API_KEY')
        if not self.api_key:
            raise ValueError("NewsAPI key is required. Set NEWS_API_KEY environment variable or pass to constructor.")
        
        self.newsapi = NewsApiClient(api_key=self.api_key)
        
        # Initialize database connection
        self.db_url = os.environ.get('DATABASE_URL')
        if not self.db_url:
            raise ValueError("DATABASE_URL environment variable is required.")
        
        # Set up data directory
        self.data_dir = os.environ.get('DATA_DIR', 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create database tables if they don't exist
        self._setup_database()
    
    def _setup_database(self):
        """Set up database tables if they don't exist."""
        conn = None
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            # Create news articles table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS news_articles (
                    id SERIAL PRIMARY KEY,
                    article_id TEXT UNIQUE,
                    source TEXT,
                    author TEXT,
                    title TEXT,
                    description TEXT,
                    url TEXT,
                    published_at TIMESTAMP,
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create sentiment table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS sentiment_analysis (
                    id SERIAL PRIMARY KEY,
                    article_id TEXT REFERENCES news_articles(article_id),
                    polarity FLOAT,
                    subjectivity FLOAT,
                    sentiment_category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create aggregate sentiment table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS aggregate_sentiment (
                    id SERIAL PRIMARY KEY,
                    date DATE UNIQUE,
                    avg_polarity FLOAT,
                    avg_subjectivity FLOAT,
                    positive_count INTEGER,
                    negative_count INTEGER,
                    neutral_count INTEGER,
                    article_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            logger.info("Database setup completed")
            
        except Exception as e:
            logger.error(f"Database setup error: {str(e)}")
            if conn:
                conn.rollback()
                
        finally:
            if conn:
                conn.close()
    
    def fetch_bitcoin_news(self, days_back: int = 7, is_free_tier: bool = True) -> List[Dict[str, Any]]:
        """
        Fetch Bitcoin-related news articles.
        
        Args:
            days_back: Number of days to look back for articles.
            is_free_tier: Whether using free tier of NewsAPI (limits to 28 days)
            
        Returns:
            List of news articles.
        """
        try:
            # Limit days_back to 28 days for free tier NewsAPI
            if is_free_tier and days_back > 28:
                limited_days = 28
                logger.warning(f"NewsAPI free tier limits historical data to 28 days. Requested {days_back} days, but using {limited_days} days.")
                days_back = limited_days
            
            # Calculate date range
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=days_back)
            
            # Format dates for NewsAPI
            from_date = start_date.strftime('%Y-%m-%d')
            to_date = end_date.strftime('%Y-%m-%d')
            
            # Search terms
            search_terms = 'bitcoin OR cryptocurrency OR crypto OR BTC'
            
            # Fetch news
            logger.info(f"Fetching news from {from_date} to {to_date} using {'free' if is_free_tier else 'paid'} tier")
            news_response = self.newsapi.get_everything(
                q=search_terms,
                from_param=from_date,
                to=to_date,
                language='en',
                sort_by='publishedAt',
                page_size=100
            )
            
            if news_response.get('status') == 'ok':
                articles = news_response.get('articles', [])
                logger.info(f"Fetched {len(articles)} Bitcoin-related news articles")
                return articles
            else:
                error_msg = news_response.get('message', 'Unknown error')
                logger.error(f"NewsAPI error: {error_msg}")
                
                # Check for common free tier errors
                if "You are trying to request results too far in the past" in error_msg:
                    logger.error("Free API tier limitation: Cannot retrieve articles older than 28 days")
                
                if "You have made too many requests" in error_msg:
                    logger.error("API rate limit exceeded. Consider upgrading to a paid plan for higher limits.")
                    
                return []
            
        except Exception as e:
            logger.error(f"Error fetching news: {str(e)}")
            return []
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text using TextBlob.
        
        Args:
            text: Text to analyze.
            
        Returns:
            Dictionary with sentiment analysis results.
        """
        if not text:
            return {
                'polarity': 0,
                'subjectivity': 0,
                'sentiment': 'neutral'
            }
        
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity
        subjectivity = analysis.sentiment.subjectivity
        
        # Determine sentiment category
        if polarity > 0.1:
            sentiment = 'positive'
        elif polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        return {
            'polarity': polarity,
            'subjectivity': subjectivity,
            'sentiment': sentiment
        }
    
    def store_articles_and_sentiment(self, articles: List[Dict[str, Any]]):
        """
        Store articles and their sentiment analysis in the database.
        
        Args:
            articles: List of news articles.
        """
        if not articles:
            logger.info("No articles to store")
            return
        
        conn = None
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            for article in articles:
                # Extract article data
                article_id = article.get('url', '')[-50:]  # Use last part of URL as ID
                source = article.get('source', {}).get('name', '')
                author = article.get('author', '')
                title = article.get('title', '')
                description = article.get('description', '')
                url = article.get('url', '')
                published_at = article.get('publishedAt', '')
                content = article.get('content', '')
                
                # Convert published_at to timestamp
                if published_at:
                    try:
                        published_at = datetime.datetime.strptime(
                            published_at, '%Y-%m-%dT%H:%M:%SZ'
                        )
                    except ValueError:
                        published_at = datetime.datetime.now()
                else:
                    published_at = datetime.datetime.now()
                
                # Store article
                cur.execute("""
                    INSERT INTO news_articles (
                        article_id, source, author, title, description,
                        url, published_at, content
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (article_id) DO NOTHING
                    RETURNING id
                """, (
                    article_id, source, author, title, description,
                    url, published_at, content
                ))
                
                # Get article ID if it was inserted
                result = cur.fetchone()
                if result:
                    # Analyze sentiment
                    text_to_analyze = f"{title} {description} {content}"
                    sentiment = self.analyze_sentiment(text_to_analyze)
                    
                    # Store sentiment analysis
                    cur.execute("""
                        INSERT INTO sentiment_analysis (
                            article_id, polarity, subjectivity, sentiment_category
                        ) VALUES (%s, %s, %s, %s)
                    """, (
                        article_id,
                        sentiment['polarity'],
                        sentiment['subjectivity'],
                        sentiment['sentiment']
                    ))
            
            conn.commit()
            logger.info(f"Stored {len(articles)} articles and their sentiment analysis")
            
            # Update aggregate sentiment
            self._update_aggregate_sentiment(cur)
            
        except Exception as e:
            logger.error(f"Error storing articles: {str(e)}")
            if conn:
                conn.rollback()
                
        finally:
            if conn:
                conn.close()
    
    def _update_aggregate_sentiment(self, cursor):
        """
        Update aggregate sentiment statistics for the current date.
        
        Args:
            cursor: Database cursor.
        """
        try:
            # Get today's date
            today = datetime.datetime.now().date()
            
            # Calculate aggregate statistics
            cursor.execute("""
                WITH daily_stats AS (
                    SELECT
                        DATE(published_at) as date,
                        AVG(polarity) as avg_polarity,
                        AVG(subjectivity) as avg_subjectivity,
                        COUNT(*) FILTER (WHERE sentiment_category = 'positive') as positive_count,
                        COUNT(*) FILTER (WHERE sentiment_category = 'negative') as negative_count,
                        COUNT(*) FILTER (WHERE sentiment_category = 'neutral') as neutral_count,
                        COUNT(*) as article_count
                    FROM news_articles na
                    JOIN sentiment_analysis sa ON na.article_id = sa.article_id
                    WHERE DATE(published_at) = %s
                    GROUP BY DATE(published_at)
                )
                INSERT INTO aggregate_sentiment (
                    date, avg_polarity, avg_subjectivity,
                    positive_count, negative_count, neutral_count,
                    article_count
                )
                SELECT
                    date, avg_polarity, avg_subjectivity,
                    positive_count, negative_count, neutral_count,
                    article_count
                FROM daily_stats
                ON CONFLICT (date) DO UPDATE
                SET
                    avg_polarity = EXCLUDED.avg_polarity,
                    avg_subjectivity = EXCLUDED.avg_subjectivity,
                    positive_count = EXCLUDED.positive_count,
                    negative_count = EXCLUDED.negative_count,
                    neutral_count = EXCLUDED.neutral_count,
                    article_count = EXCLUDED.article_count,
                    created_at = CURRENT_TIMESTAMP
            """, (today,))
            
            logger.info("Updated aggregate sentiment statistics")
            
        except Exception as e:
            logger.error(f"Error updating aggregate sentiment: {str(e)}")
            raise
    
    def get_latest_sentiment(self, days: int = 7) -> pd.DataFrame:
        """
        Get sentiment analysis results for the specified number of days.
        
        Args:
            days: Number of days to look back.
            
        Returns:
            DataFrame with sentiment analysis results.
        """
        try:
            # Calculate date range
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=days)
            
            # Query database
            conn = psycopg2.connect(self.db_url)
            query = """
                SELECT
                    DATE(published_at) as date,
                    AVG(polarity) as avg_polarity,
                    AVG(subjectivity) as avg_subjectivity,
                    COUNT(*) FILTER (WHERE sentiment_category = 'positive') as positive_count,
                    COUNT(*) FILTER (WHERE sentiment_category = 'negative') as negative_count,
                    COUNT(*) FILTER (WHERE sentiment_category = 'neutral') as neutral_count,
                    COUNT(*) as article_count
                FROM news_articles na
                JOIN sentiment_analysis sa ON na.article_id = sa.article_id
                WHERE published_at >= %s
                GROUP BY DATE(published_at)
                ORDER BY date DESC
            """
            
            df = pd.read_sql_query(query, conn, params=(start_date,))
            conn.close()
            
            # Save to CSV backup
            self._save_sentiment_to_csv(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Error getting latest sentiment: {str(e)}")
            # Try to read from CSV backup
            return self._read_sentiment_from_csv(days)
    
    def _save_sentiment_to_csv(self, df: pd.DataFrame) -> None:
        """
        Save sentiment data to CSV backup file.
        
        Args:
            df: DataFrame with sentiment data.
        """
        try:
            # Save to CSV
            csv_path = os.path.join(self.data_dir, 'sentiment_data.csv')
            df.to_csv(csv_path, index=False)
            logger.info(f"Saved sentiment data to {csv_path}")
            
        except Exception as e:
            logger.error(f"Error saving sentiment data to CSV: {str(e)}")
    
    def _read_sentiment_from_csv(self, days: int = 7) -> pd.DataFrame:
        """
        Read sentiment data from CSV backup file.
        
        Args:
            days: Number of days to look back.
            
        Returns:
            DataFrame with sentiment data.
        """
        try:
            # Calculate date range
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=days)
            
            # Read from CSV
            csv_path = os.path.join(self.data_dir, 'sentiment_data.csv')
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                df['date'] = pd.to_datetime(df['date']).dt.date
                df = df[df['date'] >= start_date.date()]
                logger.info(f"Read sentiment data from {csv_path}")
                return df
            else:
                logger.warning(f"CSV backup file not found: {csv_path}")
                return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error reading sentiment data from CSV: {str(e)}")
            return pd.DataFrame()
    
    def run_sentiment_analysis(self, days_back: int = 7, is_free_tier: bool = True):
        """
        Run the complete sentiment analysis process.
        
        Args:
            days_back: Number of days to look back for articles.
            is_free_tier: Whether using free tier of NewsAPI.
        """
        try:
            # Fetch news articles
            articles = self.fetch_bitcoin_news(days_back, is_free_tier)
            
            # Store articles and analyze sentiment
            self.store_articles_and_sentiment(articles)
            
            # Get latest sentiment results
            sentiment_df = self.get_latest_sentiment(days_back)
            
            if not sentiment_df.empty:
                logger.info("\nLatest Sentiment Analysis Results:")
                logger.info(sentiment_df.to_string())
            else:
                logger.warning("No sentiment analysis results available")
            
        except Exception as e:
            logger.error(f"Error running sentiment analysis: {str(e)}")

def main():
    """Main function to run the sentiment analyzer."""
    try:
        # Initialize analyzer
        analyzer = BitcoinSentimentAnalyzer()
        
        # Run analysis
        analyzer.run_sentiment_analysis()
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == '__main__':
    main() 