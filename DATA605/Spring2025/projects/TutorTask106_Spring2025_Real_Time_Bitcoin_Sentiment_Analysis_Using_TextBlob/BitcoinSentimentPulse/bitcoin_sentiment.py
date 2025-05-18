"""
Bitcoin Sentiment Analysis Module

This module provides direct access to Bitcoin news sentiment without database dependencies.
"""

import os
import datetime
import pandas as pd
from newsapi.newsapi_client import NewsApiClient
from textblob import TextBlob
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bitcoin_sentiment")

class BitcoinSentimentAnalyzer:
    """Simple Bitcoin sentiment analyzer using NewsAPI and TextBlob."""
    
    def __init__(self, api_key=None):
        """Initialize with NewsAPI key."""
        self.api_key = api_key or os.environ.get('NEWS_API_KEY')
        if not self.api_key:
            raise ValueError("NewsAPI key not provided and not found in environment")
        
        self.newsapi = NewsApiClient(api_key=self.api_key)
    
    def get_bitcoin_news(self, days=7, max_articles=100):
        """Get Bitcoin-related news articles from the past few days."""
        try:
            # Calculate date range
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=days)
            
            # Format dates for NewsAPI
            from_date = start_date.strftime('%Y-%m-%d')
            to_date = end_date.strftime('%Y-%m-%d')
            
            # Define Bitcoin-related search terms
            search_terms = 'bitcoin OR BTC'
            
            # Fetch news articles
            logger.info(f"Fetching Bitcoin news from {from_date} to {to_date}")
            
            # Make multiple requests if needed due to pagination limits
            all_articles = []
            page = 1
            page_size = min(100, max_articles)  # NewsAPI limits to 100 per request
            
            while len(all_articles) < max_articles:
                response = self.newsapi.get_everything(
                    q=search_terms,
                    from_param=from_date,
                    to=to_date,
                    language='en',
                    sort_by='relevancy',
                    page=page,
                    page_size=page_size
                )
                
                if response['status'] != 'ok':
                    error_msg = response.get('message', 'Unknown error')
                    logger.error(f"NewsAPI error: {error_msg}")
                    break
                
                articles = response.get('articles', [])
                if not articles:
                    break  # No more articles available
                
                all_articles.extend(articles)
                
                # Check if we need another page
                if len(articles) < page_size:
                    break  # This was the last page
                
                page += 1
            
            logger.info(f"Found {len(all_articles)} Bitcoin news articles")
            return all_articles[:max_articles]  # Limit to max requested
            
        except Exception as e:
            logger.error(f"Error fetching Bitcoin news: {str(e)}")
            return []
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of text using TextBlob."""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
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
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {
                'polarity': 0,
                'subjectivity': 0,
                'sentiment': 'neutral'
            }
    
    def get_sentiment_summary(self, days=7, max_articles=30):
        """
        Get a summary of Bitcoin sentiment from recent news.
        
        Returns:
            dict: Dictionary with sentiment summary and articles
        """
        try:
            # Get news articles
            articles = self.get_bitcoin_news(days=days, max_articles=max_articles)
            
            if not articles:
                return {
                    'status': 'error',
                    'message': 'No Bitcoin news articles found',
                    'summary': {
                        'overall_sentiment': 'Neutral',
                        'avg_polarity': 0,
                        'avg_subjectivity': 0
                    }
                }
            
            # Analyze sentiment
            analyzed_articles = []
            sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
            total_polarity = 0
            total_subjectivity = 0
            
            for article in articles:
                # Get article text components
                title = article.get('title', '')
                description = article.get('description', '')
                content = article.get('content', '')
                
                # Combine text, with title emphasized for sentiment analysis
                text = f"{title} {title} {description} {content}"
                
                # Analyze sentiment
                sentiment = self.analyze_sentiment(text)
                
                # Update counters
                sentiment_counts[sentiment['sentiment']] += 1
                total_polarity += sentiment['polarity']
                total_subjectivity += sentiment['subjectivity']
                
                # Add to analyzed articles
                analyzed_articles.append({
                    'title': title,
                    'source': article.get('source', {}).get('name', 'Unknown'),
                    'url': article.get('url', ''),
                    'published_at': article.get('publishedAt', ''),
                    'sentiment': sentiment['sentiment'],
                    'polarity': sentiment['polarity'],
                    'subjectivity': sentiment['subjectivity']
                })
            
            # Calculate averages
            article_count = len(analyzed_articles)
            avg_polarity = total_polarity / article_count if article_count > 0 else 0
            avg_subjectivity = total_subjectivity / article_count if article_count > 0 else 0
            
            # Calculate percentages
            positive_pct = (sentiment_counts['positive'] / article_count) * 100 if article_count > 0 else 0
            negative_pct = (sentiment_counts['negative'] / article_count) * 100 if article_count > 0 else 0
            neutral_pct = (sentiment_counts['neutral'] / article_count) * 100 if article_count > 0 else 0
            
            # Determine overall sentiment
            if avg_polarity > 0.1:
                overall_sentiment = 'Positive'
            elif avg_polarity < -0.1:
                overall_sentiment = 'Negative'
            else:
                overall_sentiment = 'Neutral'
            
            return {
                'status': 'success',
                'summary': {
                    'article_count': article_count,
                    'avg_polarity': avg_polarity,
                    'avg_subjectivity': avg_subjectivity,
                    'sentiment_counts': sentiment_counts,
                    'overall_sentiment': overall_sentiment,
                    'positive_pct': positive_pct,
                    'negative_pct': negative_pct,
                    'neutral_pct': neutral_pct,
                    'date': datetime.datetime.now().strftime('%Y-%m-%d')
                },
                'articles': analyzed_articles
            }
            
        except Exception as e:
            logger.error(f"Error getting sentiment summary: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'summary': {
                    'overall_sentiment': 'Neutral',
                    'avg_polarity': 0,
                    'avg_subjectivity': 0
                }
            }
    
    def get_sentiment_dataframe(self, days=7, max_articles=30):
        """
        Get a DataFrame with sentiment data for Bitcoin news.
        
        Returns:
            pd.DataFrame: DataFrame with sentiment data by date
        """
        results = self.get_sentiment_summary(days=days, max_articles=max_articles)
        
        if results['status'] != 'success':
            return pd.DataFrame()
            
        # Group articles by date
        articles = results['articles']
        date_sentiments = {}
        
        for article in articles:
            # Parse published date
            try:
                published_date = datetime.datetime.strptime(
                    article['published_at'].split('T')[0], 
                    '%Y-%m-%d'
                ).date()
            except (ValueError, AttributeError, IndexError):
                # If date parsing fails, use current date
                published_date = datetime.datetime.now().date()
            
            # Initialize if not exists
            if published_date not in date_sentiments:
                date_sentiments[published_date] = {
                    'polarity_sum': 0,
                    'subjectivity_sum': 0,
                    'positive_count': 0,
                    'negative_count': 0,
                    'neutral_count': 0,
                    'article_count': 0
                }
            
            # Update counts
            date_sentiments[published_date]['polarity_sum'] += article['polarity']
            date_sentiments[published_date]['subjectivity_sum'] += article['subjectivity']
            date_sentiments[published_date][f"{article['sentiment']}_count"] += 1
            date_sentiments[published_date]['article_count'] += 1
        
        # Convert to DataFrame
        df_data = []
        
        for date, stats in date_sentiments.items():
            article_count = stats['article_count']
            if article_count > 0:
                avg_polarity = stats['polarity_sum'] / article_count
                avg_subjectivity = stats['subjectivity_sum'] / article_count
            else:
                avg_polarity = 0
                avg_subjectivity = 0
                
            df_data.append({
                'date': date,
                'avg_polarity': avg_polarity,
                'avg_subjectivity': avg_subjectivity,
                'positive_count': stats['positive_count'],
                'negative_count': stats['negative_count'],
                'neutral_count': stats['neutral_count'],
                'article_count': article_count
            })
        
        # Create DataFrame and sort by date
        df = pd.DataFrame(df_data)
        if not df.empty:
            df = df.sort_values(by='date')
            
        return df

# Simple test function
def test_sentiment():
    """Test the Bitcoin sentiment analyzer."""
    try:
        analyzer = BitcoinSentimentAnalyzer()
        results = analyzer.get_sentiment_summary(days=3, max_articles=5)
        
        if results['status'] == 'success':
            print(f"Analysis successful! Found {results['summary']['article_count']} articles")
            print(f"Overall sentiment: {results['summary']['overall_sentiment']}")
            print(f"Average polarity: {results['summary']['avg_polarity']:.2f}")
            
            print("\nSample articles:")
            for i, article in enumerate(results['articles'][:3]):
                print(f"{i+1}. {article['title']}")
                print(f"   Sentiment: {article['sentiment']} ({article['polarity']:.2f})")
                print(f"   Source: {article['source']}")
                print()
        else:
            print(f"Error: {results['message']}")
            
    except Exception as e:
        print(f"Test failed: {str(e)}")

if __name__ == "__main__":
    test_sentiment()