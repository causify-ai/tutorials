"""
template_utils.py

This file contains utility functions that support the tutorial notebooks.

- Notebooks should call these functions instead of writing raw logic inline.
- This helps keep the notebooks clean, modular, and easier to debug.
- Students should implement functions here for data preprocessing,
  model setup, evaluation, or any reusable logic.
"""

# bitcoin_utils.py

from transformers import pipeline
from typing import List

# Initialize HuggingFace pipelines
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
sentiment_analyzer = pipeline("sentiment-analysis")

def fetch_news() -> List[str]:
    """
    Fetch Bitcoin news articles.

    :return: A list of Bitcoin news article texts.
    """
    news_list = [
        "Bitcoin surges above $30,000 as investors show renewed interest.",
        "Cryptocurrency markets remain volatile amid regulatory concerns."
    ]
    return news_list

def summarize_article(text: str) -> str:
    """
    Summarize a Bitcoin news article.

    :param text: The full article text.
    :return: The summarized version of the article.
    """
    summary = summarizer(text, max_length=60, min_length=20, do_sample=False)
    return summary[0]['summary_text']

def analyze_sentiment(text: str) -> str:
    """
    Analyze the sentiment of a Bitcoin news article.

    :param text: The full article text.
    :return: Sentiment label (POSITIVE, NEGATIVE, or NEUTRAL).
    """
    result = sentiment_analyzer(text)
    return result[0]['label']
import requests
from typing import List

def fetch_bitcoin_news_from_newsapi(api_key: str, query: str = "bitcoin", page_size: int = 5,
                                    from_date: str = None, to_date: str = None) -> List[dict]:
    url = f"https://newsapi.org/v2/everything?q={query}&pageSize={page_size}&sortBy=publishedAt&language=en&apiKey={api_key}"
    if from_date and to_date:
        url += f"&from={from_date}&to={to_date}"

    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"NewsAPI request failed: {response.status_code}")
    data = response.json()
    return data.get("articles", [])


from typing import List

def fetch_bitcoin_news_multiple_pages(api_key: str, query: str = "bitcoin", total_articles: int = 200) -> List[dict]:
    all_articles = []
    page_size = 100
    pages = (total_articles + page_size - 1) // page_size  # Number of pages

    for page in range(1, pages + 1):
        url = f"https://newsapi.org/v2/everything?q={query}&pageSize={page_size}&page={page}&sortBy=publishedAt&language=en&apiKey={api_key}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch page {page}: {response.status_code}")
            break
        data = response.json()
        articles = data.get("articles", [])
        all_articles.extend(articles)  # Keep entire article dicts

    return all_articles




def summarize_and_analyze_articles(articles: List[dict]) -> List[dict]:
    results = []
    for article in articles:
        content = article.get("content") or article.get("description")
        if not content:
            continue
        summary = summarize_article(content)
        sentiment = analyze_sentiment(content)
        results.append({
            "original": content,
            "summary": summary,
            "sentiment": sentiment,
            "publishedAt": article.get("publishedAt")
        })
    return results

