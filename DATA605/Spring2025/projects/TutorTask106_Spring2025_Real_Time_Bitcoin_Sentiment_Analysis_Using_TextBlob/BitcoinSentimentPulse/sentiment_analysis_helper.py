"""
Sentiment Analysis Helper Module

This module provides a simplified interface to run Bitcoin sentiment analysis
without the full overhead of the main sentiment analyzer class.
"""

import os
import pandas as pd
import psycopg2
from textblob import TextBlob
from newsapi.newsapi_client import NewsApiClient
import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('sentiment_helper')

def analyze_sentiment_for_article(title, description, content):
    """
    Analyze sentiment of a news article using TextBlob.
    
    Args:
        title: Article title
        description: Article description
        content: Article content
    
    Returns:
        Dictionary with sentiment analysis results
    """
    # Combine text for analysis, giving more weight to title
    text = f"{title} {title} {description} {content or ''}"
    
    # Analyze with TextBlob
    blob = TextBlob(text)
    
    # Get polarity (-1 to 1) and subjectivity (0 to 1)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    
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

def get_top_bitcoin_sentiment(api_key=None, num_articles=10):
    """
    Get sentiment analysis for top recent Bitcoin news articles.
    
    Args:
        api_key: NewsAPI key (optional, will use env var if not provided)
        num_articles: Number of articles to analyze
    
    Returns:
        Dictionary with sentiment summary and articles
    """
    # Use provided API key or get from environment
    api_key = api_key or os.environ.get('NEWS_API_KEY')
    
    if not api_key:
        logger.error("NewsAPI key not available")
        return {
            'status': 'error',
            'message': 'NewsAPI key not available'
        }
    
    try:
        # Initialize NewsAPI client
        newsapi = NewsApiClient(api_key=api_key)
        
        # Set date range (last 7 days)
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=7)
        
        # Format dates for NewsAPI
        from_date = start_date.strftime('%Y-%m-%d')
        to_date = end_date.strftime('%Y-%m-%d')
        
        # Search terms for Bitcoin
        search_terms = 'bitcoin OR cryptocurrency OR crypto OR BTC'
        
        # Fetch news articles
        logger.info(f"Fetching top {num_articles} Bitcoin news articles...")
        news_response = newsapi.get_everything(
            q=search_terms,
            from_param=from_date,
            to=to_date,
            language='en',
            sort_by='relevancy',
            page_size=num_articles
        )
        
        if news_response.get('status') != 'ok':
            logger.error(f"NewsAPI error: {news_response.get('message', 'Unknown error')}")
            return {
                'status': 'error',
                'message': f"NewsAPI error: {news_response.get('message', 'Unknown error')}"
            }
        
        articles = news_response.get('articles', [])
        logger.info(f"Fetched {len(articles)} articles")
        
        if not articles:
            return {
                'status': 'warning',
                'message': 'No articles found'
            }
        
        # Analyze sentiment for each article
        analyzed_articles = []
        
        # Counters for sentiment distribution
        sentiment_counts = {
            'positive': 0,
            'negative': 0,
            'neutral': 0
        }
        
        # For calculating averages
        total_polarity = 0
        total_subjectivity = 0
        
        for article in articles:
            # Extract article text components
            title = article.get('title', '')
            description = article.get('description', '')
            content = article.get('content', '')
            
            # Analyze sentiment
            sentiment_result = analyze_sentiment_for_article(title, description, content)
            
            # Update counters
            sentiment_counts[sentiment_result['sentiment']] += 1
            total_polarity += sentiment_result['polarity']
            total_subjectivity += sentiment_result['subjectivity']
            
            # Add to analyzed articles
            analyzed_articles.append({
                'title': title,
                'source': article.get('source', {}).get('name', 'Unknown'),
                'url': article.get('url', ''),
                'published_at': article.get('publishedAt', ''),
                'sentiment': sentiment_result['sentiment'],
                'polarity': sentiment_result['polarity'],
                'subjectivity': sentiment_result['subjectivity']
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
                'neutral_pct': neutral_pct
            },
            'articles': analyzed_articles
        }
    
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {str(e)}")
        return {
            'status': 'error',
            'message': f"Error analyzing sentiment: {str(e)}"
        }

def update_sentiment_display(st, container):
    """
    Update sentiment display in a Streamlit app.
    
    Args:
        st: Streamlit module
        container: Streamlit container to update
    """
    try:
        with container:
            st.write("### Bitcoin Sentiment Analysis")
            
            with st.spinner("Analyzing recent Bitcoin news sentiment..."):
                # Get sentiment analysis for top 15 articles
                sentiment_data = get_top_bitcoin_sentiment(num_articles=15)
                
                if sentiment_data['status'] == 'success':
                    # Display summary
                    summary = sentiment_data['summary']
                    
                    # Color for overall sentiment
                    sentiment_color = {
                        'Positive': 'green',
                        'Negative': 'red',
                        'Neutral': 'gray'
                    }.get(summary['overall_sentiment'], 'gray')
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "Overall Sentiment", 
                            summary['overall_sentiment'],
                            f"{summary['avg_polarity']:.2f}"
                        )
                    
                    with col2:
                        st.metric(
                            "Articles Analyzed", 
                            summary['article_count']
                        )
                    
                    with col3:
                        st.metric(
                            "Average Subjectivity", 
                            f"{summary['avg_subjectivity']:.2f}"
                        )
                    
                    # Distribution chart
                    st.write("#### Sentiment Distribution")
                    
                    # Create sentiment distribution
                    sentiment_distribution = {
                        'Positive': summary['positive_pct'],
                        'Neutral': summary['neutral_pct'],
                        'Negative': summary['negative_pct']
                    }
                    
                    # Create chart using st.bar_chart
                    chart_data = pd.DataFrame({
                        'Percentage': [
                            sentiment_distribution['Positive'],
                            sentiment_distribution['Neutral'],
                            sentiment_distribution['Negative']
                        ]
                    }, index=['Positive', 'Neutral', 'Negative'])
                    
                    st.bar_chart(chart_data)
                    
                    # Recent news articles
                    st.write("#### Recent Bitcoin News")
                    
                    for i, article in enumerate(sentiment_data['articles'][:5]):
                        sentiment_emoji = {
                            'positive': '😀',
                            'neutral': '😐',
                            'negative': '😟'
                        }.get(article['sentiment'], '')
                        
                        st.write(f"{sentiment_emoji} **{article['title']}**")
                        st.write(f"Source: {article['source']} | Published: {article['published_at']}")
                        st.write(f"Sentiment: {article['sentiment'].capitalize()} ({article['polarity']:.2f})")
                        st.write(f"[Read More]({article['url']})")
                        
                        if i < len(sentiment_data['articles']) - 1:
                            st.write("---")
                
                elif sentiment_data['status'] == 'warning':
                    st.warning(sentiment_data['message'])
                
                else:
                    st.error(sentiment_data['message'])
    
    except Exception as e:
        st.error(f"Error updating sentiment display: {str(e)}")