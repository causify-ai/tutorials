"""
Sentiment analysis module for cryptocurrency news.
Analyzes sentiment of news articles to provide market sentiment insights.
"""

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
import logging
from typing import List, Dict, Any, Optional
import datetime

# Download VADER lexicon if not already downloaded
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

logger = logging.getLogger(__name__)

class CryptoSentimentAnalyzer:
    """Analyzes sentiment of cryptocurrency news articles."""
    
    def __init__(self):
        """Initialize the sentiment analyzer."""
        self.analyzer = SentimentIntensityAnalyzer()
        self.sentiment_history = {}
        
    def analyze_article(self, text: str) -> Dict[str, float]:
        """
        Analyze the sentiment of a single article.
        
        Args:
            text: The article text to analyze
            
        Returns:
            Dictionary with sentiment scores
        """
        if not text:
            return {"compound": 0, "pos": 0, "neu": 0, "neg": 0}
            
        return self.analyzer.polarity_scores(text)
    
    def analyze_news_batch(self, news_data: List[Dict]) -> Dict[str, Any]:
        """
        Analyze sentiment for a batch of news articles.
        
        Args:
            news_data: List of news article dictionaries
            
        Returns:
            Dictionary with sentiment analysis results
        """
        if not news_data:
            return {"overall_sentiment": "neutral", "score": 0, "articles_analyzed": 0}
            
        total_compound = 0
        sentiment_scores = []
        
        for article in news_data:
            title = article.get('title', '')
            description = article.get('description', '')
            content = article.get('content', '')
            
            # Analyze title with double weight as it's most impactful
            title_sentiment = self.analyze_article(title)
            desc_sentiment = self.analyze_article(description)
            content_sentiment = self.analyze_article(content)
            
            # Calculate weighted score (title has more impact)
            compound_score = (
                title_sentiment['compound'] * 0.5 + 
                desc_sentiment['compound'] * 0.3 + 
                content_sentiment['compound'] * 0.2
            )
            
            # Store sentiment data
            sentiment_data = {
                'title': title,
                'source': article.get('source', {}).get('name', 'Unknown'),
                'published': article.get('publishedAt', 'Unknown'),
                'compound_score': compound_score,
                'sentiment': self._get_sentiment_label(compound_score)
            }
            
            sentiment_scores.append(sentiment_data)
            total_compound += compound_score
        
        # Calculate overall sentiment
        avg_compound = total_compound / len(news_data) if news_data else 0
        overall_sentiment = self._get_sentiment_label(avg_compound)
        
        # Store in history with timestamp
        timestamp = datetime.datetime.now().isoformat()
        self.sentiment_history[timestamp] = {
            'overall_sentiment': overall_sentiment,
            'score': avg_compound,
            'articles_analyzed': len(news_data)
        }
        
        return {
            'overall_sentiment': overall_sentiment,
            'score': avg_compound,
            'articles_analyzed': len(news_data),
            'article_sentiments': sentiment_scores,
            'timestamp': timestamp
        }
    
    def _get_sentiment_label(self, compound_score: float) -> str:
        """Convert compound score to sentiment label."""
        if compound_score >= 0.05:
            return "positive"
        elif compound_score <= -0.05:
            return "negative"
        else:
            return "neutral"
    
    def get_sentiment_trend(self, days: int = 7) -> Dict[str, Any]:
        """
        Calculate sentiment trend over a period of time.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with sentiment trend analysis
        """
        if not self.sentiment_history:
            return {"trend": "neutral", "data": []}
            
        # Filter history by date
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
        recent_sentiments = {
            ts: data for ts, data in self.sentiment_history.items() 
            if datetime.datetime.fromisoformat(ts) >= cutoff_date
        }
        
        if not recent_sentiments:
            return {"trend": "neutral", "data": []}
            
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame([
            {
                'timestamp': ts,
                'score': data['score'],
                'sentiment': data['overall_sentiment']
            }
            for ts, data in recent_sentiments.items()
        ])
        
        # Sort by timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Calculate trend
        if len(df) >= 2:
            first_half = df.iloc[:len(df)//2]['score'].mean()
            second_half = df.iloc[len(df)//2:]['score'].mean()
            trend_direction = second_half - first_half
            
            if trend_direction > 0.1:
                trend = "improving"
            elif trend_direction < -0.1:
                trend = "deteriorating"
            else:
                trend = "stable"
        else:
            trend = "insufficient data"
        
        # Calculate sentiment distribution
        sentiment_counts = df['sentiment'].value_counts().to_dict()
        
        return {
            "trend": trend,
            "avg_score": df['score'].mean(),
            "distribution": sentiment_counts,
            "data_points": len(df),
            "period_days": days,
            "data": df.to_dict(orient='records')
        }