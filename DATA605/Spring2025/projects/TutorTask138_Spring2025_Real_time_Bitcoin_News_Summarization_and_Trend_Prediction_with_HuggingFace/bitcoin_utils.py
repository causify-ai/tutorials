"""
bitcoin_utils.py

Utility module to support real-time Bitcoin news summarization and sentiment analysis
using HuggingFace and NewsAPI. Designed to generate structured sentiment data
for time series modeling and prediction.
"""

import requests
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from transformers import pipeline
import time
import pandas as pd

# Initialize HuggingFace NLP pipelines
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
sentiment_analyzer = pipeline("sentiment-analysis")



def summarize_article(text: str) -> str:
    """
    Summarize a block of text using HuggingFace's summarization model.

    :param text: Full article text or description
    :return: Summarized text
    """
    try:
        summary = summarizer(text, max_length=60, min_length=20, do_sample=False)
        return summary[0]['summary_text']
    except Exception:
        return ""

def analyze_sentiment(text: str) -> str:
    """
    Analyze sentiment using HuggingFace's sentiment analysis model.

    :param text: Text to classify
    :return: Sentiment label (POSITIVE, NEGATIVE, NEUTRAL)
    """
    try:
        result = sentiment_analyzer(text)
        return result[0]['label']
    except Exception:
        return "NEUTRAL"
    


def get_100_summarized_articles(api_key: str) -> pd.DataFrame:
    """
    Fetch, summarize, and analyze 100 Bitcoin news articles from the past 30 days.

    :param api_key: NewsAPI key
    :return: DataFrame with published_date, title, summary, sentiment, source
    """
    from datetime import datetime, timedelta

    results = []
    total_fetched = 0
    yesterday = datetime.utcnow().date() - timedelta(days=1)

    for i in range(30):
        if total_fetched >= 100:
            break

        date = yesterday - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")

        url = (
            f"https://newsapi.org/v2/everything?q=bitcoin"
            f"&from={date_str}&to={date_str}"
            f"&pageSize=5&sortBy=publishedAt"
            f"&language=en&apiKey={api_key}"
        )

        response = requests.get(url)
        if response.status_code != 200:
            continue

        articles = response.json().get("articles", [])
        for article in articles:
            if total_fetched >= 100:
                break

            content = article.get("content") or article.get("description") or ""
            summary = summarize_article(content)
            sentiment = analyze_sentiment(summary)

            results.append({
                "published_date": article.get("publishedAt", "")[:10],
                "title": article.get("title", ""),
                "summary": summary,
                "sentiment": sentiment,
                "source": article.get("source", {}).get("name", "")
            })

            total_fetched += 1
            time.sleep(1)

    return pd.DataFrame(results)
