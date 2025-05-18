"""
Real-time Bitcoin sentiment analysis script.

This script updates the sentiment analysis data in the database
by fetching recent Bitcoin news from NewsAPI and analyzing sentiment.
"""

import os
import sys
from sentiment_analysis.sentiment_analyzer import BitcoinSentimentAnalyzer
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('update_sentiment')

def main():
    """Run the sentiment analysis update."""
    try:
        logger.info("Starting Bitcoin sentiment analysis update...")
        
        # Initialize analyzer with NewsAPI key from environment variable
        api_key = os.environ.get('NEWS_API_KEY')
        if not api_key:
            logger.error("NEWS_API_KEY environment variable not set. Can't proceed.")
            return 1
            
        # Create sentiment analyzer
        analyzer = BitcoinSentimentAnalyzer(api_key=api_key)
        
        # Get the number of days to analyze from command line or default to 7
        days_back = 7
        if len(sys.argv) > 1:
            try:
                days_back = int(sys.argv[1])
                if days_back < 1 or days_back > 28:
                    logger.warning("Days must be between 1 and 28 for free tier. Using 7 days.")
                    days_back = 7
            except ValueError:
                logger.warning(f"Invalid days argument: {sys.argv[1]}. Using 7 days.")
        
        logger.info(f"Analyzing Bitcoin news sentiment for the past {days_back} days...")
        
        # Run the sentiment analysis
        articles = analyzer.fetch_bitcoin_news(days_back=days_back, is_free_tier=True)
        
        if not articles:
            logger.warning("No Bitcoin news articles found.")
            return 0
            
        logger.info(f"Found {len(articles)} Bitcoin news articles. Analyzing sentiment...")
        
        # Store analysis in database
        analyzer.store_articles_and_sentiment(articles)
        logger.info("Articles and sentiment stored in database.")
        
        # Update aggregate sentiment stats
        logger.info("Updating aggregate sentiment statistics...")
        with analyzer._get_db_connection() as conn:
            with conn.cursor() as cursor:
                analyzer._update_aggregate_sentiment(cursor)
            conn.commit()
            
        logger.info("Sentiment analysis update completed successfully.")
        return 0
    
    except Exception as e:
        logger.error(f"Error updating sentiment: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())