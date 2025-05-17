import os
import json
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
import re

import requests
import pandas as pd
from dotenv import load_dotenv
import tiktoken
from litellm import completion

# For visualization
import plotly.express as px
import plotly.graph_objects as go
from IPython.display import HTML
import ipywidgets as widgets

# For notebook generation (not currently used)
# import nbformat as nbf
# from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell


@dataclass
class Config:
    """Configuration settings for the application."""
    NEWS_API_KEY: str
    OPENAI_API_KEY: Optional[str]
    TOGETHER_API_KEY: Optional[str]
    GOOGLE_API_KEY: Optional[str]
    HUGGINGFACE_API_KEY: Optional[str]
    PROVIDER: str = "together_ai"
    MODEL_ID: str = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    MAX_TOKENS: int = 10000
    DATA_DIR: Path = Path.cwd() / "data"
    CSV_PATH: Path = DATA_DIR / "bitcoin_news_sentiment.csv"
    CACHE_PATH: Path = DATA_DIR / "article_cache.json"
    PROMPT_TEMPLATE: str = (
        "You are a financial sentiment analyst.\n"
    "Classify the sentiment of the following Bitcoin news article as exactly one of these three words: Positive, Neutral, Negative.\n"
    "Respond with ONLY one of these three words. Do not include any other words, punctuation, or explanation.\n\n"
    "Article: {text}\n\n"
    "Sentiment:"
    )

    @classmethod
    def load(cls) -> 'Config':
        """Load configuration from environment variables."""
        load_dotenv()
        
        if not os.getenv("NEWS_API_KEY"):
            raise RuntimeError("NEWS_API_KEY is not set – please export it or add to .env")
            
        return cls(
            NEWS_API_KEY=os.getenv("NEWS_API_KEY", ""),
            OPENAI_API_KEY=os.getenv("OPENAI_API_KEY"),
            TOGETHER_API_KEY=os.getenv("TOGETHER_API_KEY"),
            GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY"),
            HUGGINGFACE_API_KEY=os.getenv("HUGGINGFACE_API_KEY"),
        )

    @property
    def provider_configs(self) -> Dict[str, Dict]:
        """Get provider-specific configurations."""
        return {
            "together_ai": {
                "model": "together_ai/mistralai/Mixtral-8x7B-Instruct-v0.1",
                "api_key": self.TOGETHER_API_KEY,
            },
            "openai": {
                "model": "openai/gpt-3.5-turbo",
                "api_key": self.OPENAI_API_KEY,
            },
            "huggingface": {
                "model": "huggingface/HuggingFaceH4/zephyr-7b-beta",
                "api_key": self.HUGGINGFACE_API_KEY,
            },
            "gemini": {
                "model": "gemini-pro",
                "api_key": self.GOOGLE_API_KEY,
            },
            "ollama": {
                "model": "ollama/llama2",
                "api_key": None,
            },
        }


def fetch_bitcoin_news(config: Config, page_size: int = 10, days_back: int = 1, custom_from_date: str = None, custom_to_date: str = None) -> List[Dict]:
    """Fetch Bitcoin news articles from NewsAPI within a date range.
    
    Args:
        config: Configuration object with API keys
        page_size: Number of articles to fetch
        days_back: Number of days in the past to fetch articles from (default: 1)
        custom_from_date: Optional specific start date in YYYY-MM-DD format
        custom_to_date: Optional specific end date in YYYY-MM-DD format
    
    Returns:
        List of article dictionaries
    """
    url = 'https://newsapi.org/v2/everything'
    
    # Set up date range
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Use custom dates if provided, otherwise calculate based on days_back
    if custom_from_date:
        from_date = custom_from_date
    else:
        from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    to_date = custom_to_date if custom_to_date else today
    
    params = {
        'q': 'Bitcoin',
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': page_size,
        'from': from_date,
        'to': to_date,
        'apiKey': config.NEWS_API_KEY,
    }
    
    print(f"Fetching Bitcoin news from {from_date} to {to_date}...")
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json().get('articles', [])


def count_tokens(text: str) -> int:
    """Count the number of tokens in a text string."""
    encoding = tiktoken.get_encoding('cl100k_base')
    return len(encoding.encode(text))


def truncate_text(text: str, max_tokens: int = 1000) -> str:
    """Truncate text to fit within token limit, preserving complete sentences."""
    if count_tokens(text) <= max_tokens:
        return text
    sentences = text.split('. ')
    truncated = []
    current_tokens = 0
    
    for sentence in sentences:
        sentence_tokens = count_tokens(sentence)
        if current_tokens + sentence_tokens <= max_tokens:
            truncated.append(sentence)
            current_tokens += sentence_tokens
        else:
            break
    
    return '. '.join(truncated) + '.'


def classify_sentiment(text: str, config: Config) -> Tuple[str, float]:
    """Analyze sentiment using LiteLLM."""
    truncated_text = truncate_text(text, config.MAX_TOKENS)
    prompt = config.PROMPT_TEMPLATE.format(text=truncated_text.strip())
    provider_config = config.provider_configs[config.PROVIDER]
    
    try:
        response = completion(
            model=provider_config['model'],
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0,
            max_tokens=1,
            api_key=provider_config.get('api_key'),
        )
        result = response.choices[0].message.content.strip().split()[0]
        return result, 0.0  # Cost is handled by LiteLLM
    except Exception as e:
        print(f"Error with {config.PROVIDER} provider: {str(e)}")
        return "Neutral", 0.0


def process_news_articles(config: Config, page_size: int = 10, days_back: int = 1, custom_from_date: str = None, custom_to_date: str = None) -> pd.DataFrame:
    """Process news articles and analyze sentiment.
    
    Args:
        config: Configuration object
        page_size: Number of articles to fetch
        days_back: Number of days in the past to fetch articles from
        custom_from_date: Optional specific start date in YYYY-MM-DD format
        custom_to_date: Optional specific end date in YYYY-MM-DD format
        
    Returns:
        DataFrame with processed articles and sentiment analysis
    """
    # Create the data directory if it doesn't exist
    config.DATA_DIR.mkdir(exist_ok=True)
    
    # Initialize cache
    cache = {}
    if config.CACHE_PATH.exists():
        try:
            with open(config.CACHE_PATH, 'r') as f:
                cache = json.load(f)
        except json.JSONDecodeError:
            print("Warning: Could not parse cache file. Starting with empty cache.")
    
    articles = fetch_bitcoin_news(
        config, 
        page_size=page_size, 
        days_back=days_back,
        custom_from_date=custom_from_date,
        custom_to_date=custom_to_date
    )
    
    rows = []
    total_cost = 0.0
    new_cache_entries = 0

    # Print the number of articles fetched
    print(f"Fetched {len(articles)} articles")
    
    for art in articles:
        headline = art.get('title', '').strip()
        content = art.get('description', '') or art.get('content', '')
        if not content:
            continue
        
        # Generate a unique identifier for the article
        article_hash = hashlib.md5(f"{headline}{content}".encode()).hexdigest()
        
        # Check if the article is already in the cache
        if article_hash in cache:
            cached_data = cache[article_hash]
            # Normalize cached sentiment
            sentiment_lower = str(cached_data['sentiment']).lower()
            if sentiment_lower in ['pos', 'positive']:
                sentiment_norm = 'Pos'
                score = 1
            elif sentiment_lower in ['neg', 'negative']:
                sentiment_norm = 'Neg'
                score = -1
            elif sentiment_lower in ['n', 'ne', 'neutral']:
                sentiment_norm = 'N'
                score = 0
            else:
                sentiment_norm = 'N'
                score = 0
            rows.append({
                'publishedAt': art.get('publishedAt'),
                'headline': headline,
                'sentiment': sentiment_norm,
                'score': score,
                'url': art.get('url'),
                'cost': 0.0,  # No cost for cached results
                'cached': True
            })
            print(f"[CACHED] [{sentiment_norm}] {headline[:80]}...")
            continue
        
        # Analyze sentiment for new articles
        sentiment, cost = classify_sentiment(content, config)
        print(f"Raw sentiment from model: '{sentiment}' for headline: {headline[:80]}")
        total_cost += cost
        # Robust normalization
        sentiment_lower = re.sub(r'[^a-z]', '', sentiment.lower())  # Remove non-letters
        if sentiment_lower in ['pos', 'positive']:
            score = 1
            sentiment_norm = 'Pos'
        elif sentiment_lower in ['neg', 'negative']:
            score = -1
            sentiment_norm = 'Neg'
        elif sentiment_lower in ['n', 'ne', 'neutral']:
            score = 0
            sentiment_norm = 'N'
        else:
            score = 0
            sentiment_norm = 'N'  # Default to Neutral
        
        # Add to cache
        cache[article_hash] = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'sentiment': sentiment_norm,
            'score': score
        }
        new_cache_entries += 1
        
        rows.append({
            'publishedAt': art.get('publishedAt'),
            'headline': headline,
            'sentiment': sentiment_norm,
            'score': score,
            'url': art.get('url'),
            'cost': cost,
            'cached': False
        })
        print(f"[NEW] [{sentiment_norm}] {headline[:80]}...")

    # Save the updated cache
    if new_cache_entries > 0:
        with open(config.CACHE_PATH, 'w') as f:
            json.dump(cache, f, indent=2)
        print(f"Cache updated with {new_cache_entries} new entries.")

    df = pd.DataFrame(rows)
    if not df.empty:
        df['publishedAt'] = pd.to_datetime(df['publishedAt'])
        df = df.sort_values('publishedAt', ascending=False)
        df.reset_index(drop=True, inplace=True)
        # Normalize sentiment labels in the DataFrame to 'Pos', 'Neg', 'Ne'
        sentiment_map = {
            'Pos': 'Pos',
            'pos': 'Pos',
            'Positive': 'Pos',
            'positive': 'Pos',
            'Neg': 'Neg',
            'neg': 'Neg',
            'Negative': 'Neg',
            'negative': 'Neg',
            'N': 'Ne',
            'n': 'Ne',
            'Ne': 'Ne',
            'ne': 'Ne',
            'Neutral': 'Ne',
            'neutral': 'Ne'
        }
        df['sentiment'] = df['sentiment'].map(lambda x: sentiment_map.get(str(x).strip(), 'Ne'))
    
    cached_count = df['cached'].sum() if 'cached' in df.columns else 0
    print(f"Articles processed: {len(df)} (New: {len(df) - cached_count}, Cached: {cached_count})")
    print(f"Total cost: ${total_cost:.6f}")
    return df


def make_clickable(val):
    """Make URL clickable in HTML."""
    return f'<a href="{val}" target="_blank">Link</a>' if pd.notnull(val) else ''


def create_sentiment_pie_chart(df: pd.DataFrame) -> go.Figure:
    """Create a pie chart of sentiment distribution."""
    return px.pie(
        values=df['sentiment'].value_counts().values,
        names=df['sentiment'].value_counts().index,
        title='Sentiment Distribution',
        color=df['sentiment'].value_counts().index,
        color_discrete_map={'Positive': 'green', 'Neutral': 'gray', 'Negative': 'red'}
    )


