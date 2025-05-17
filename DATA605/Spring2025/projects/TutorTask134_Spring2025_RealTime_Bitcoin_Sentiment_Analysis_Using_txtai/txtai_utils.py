"""
txtai_utils.py

Utility functions and classes for the Real-Time Bitcoin Sentiment Analysis project.

- Provides modular functions for fetching news data, performing sentiment analysis,
  and building semantic search with txtai.
- Keeps notebooks clean and reusable.
"""

import os
import logging
import requests
from transformers import pipeline
from statsmodels.tsa.arima.model import ARIMA
import pandas as pd
import matplotlib.pyplot as plt

# Fix txtai's internal translation module crash
os.environ["TRANSFORMERS_NO_ADVISORY_WARNINGS"] = "true"

# Import only the part of txtai we need
from txtai.embeddings import Embeddings

# --------------------------------------------------------------------------
# Logging Setup
# --------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------
# Function: Fetch real-time Bitcoin news using NewsAPI
# --------------------------------------------------------------------------

def fetch_bitcoin_headlines(api_key, query="bitcoin", max_articles=100):
    """
    Fetches recent Bitcoin-related news headlines from NewsAPI.

    :param api_key: Your NewsAPI key
    :param query: Search term (default = "bitcoin")
    :param max_articles: Max number of headlines to fetch
    :return: List of headline strings
    """
    logger.info("Fetching Bitcoin news headlines from NewsAPI...")
    url = (
        f"https://newsapi.org/v2/everything?"
        f"q={query}&language=en&sortBy=publishedAt&pageSize={max_articles}"
        f"&apiKey={api_key}"
    )
    response = requests.get(url)
    response.raise_for_status()
    articles = response.json().get("articles", [])
    headlines = [article["title"] for article in articles if article.get("title")]

    logger.info(f"Fetched {len(headlines)} headlines.")
    return headlines

# --------------------------------------------------------------------------
# Class: Semantic search using txtai embeddings
# --------------------------------------------------------------------------

class TxtaiSentimentSearch:
    """
    Builds a txtai semantic search engine from a list of headlines.
    """

    def __init__(self, model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initializes txtai embeddings with the specified model.

        :param model: Hugging Face model for embedding (default = all-MiniLM)
        """
        logger.info("Initializing txtai semantic search engine...")
        self.index = Embeddings({"path": model})
        self.sentences = []

    def build_index(self, data):
        """
        Builds a semantic index from a list of text.
        """
        self.sentences = data
        documents = [(i, text, None) for i, text in enumerate(data)]
        self.index.index(documents)
        logger.info(f"Built index with {len(data)} documents.")

    def search(self, query, top_k=3):
        """
        Performs semantic search on the indexed headlines.

        :param query: Natural language question
        :param top_k: Number of top matches to return
        :return: List of top matched sentences
        """
        results = self.index.search(query, top_k)
        logger.info(f"Search complete for query: '{query}'")
        return [self.sentences[i] for i, _ in results]

# --------------------------------------------------------------------------
# Function: Perform sentiment analysis using transformers
# --------------------------------------------------------------------------

def analyze_sentiment(headline):
    """
    Analyzes sentiment of a single headline using Hugging Face pipeline.

    :param headline: News headline (string)
    :return: Sentiment label (e.g., POSITIVE or NEGATIVE)
    """
    logger.info("Loading sentiment pipeline...")
    sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    result = sentiment_pipeline(headline)[0]
    logger.info(f"Analyzed: '{headline}' → {result['label']} ({result['score']:.2f})")
    return result['label']
# --------------------------------------------------------------------------
# Function: Run ARIMA Forecast on Bitcoin Price Data
# --------------------------------------------------------------------------


def run_arima_forecast(df, column='price', order=(2, 1, 2), steps=7):
    """
    Runs an ARIMA forecast on a specified column of a DataFrame.

    :param df: DataFrame with datetime index
    :param column: Column to forecast (default = 'price')
    :param order: ARIMA model order (p,d,q)
    :param steps: Number of days to forecast
    :return: DataFrame with forecasted values
    """
    logger.info(f"Running ARIMA forecast on '{column}' column...")

    model = ARIMA(df[column], order=order)
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=steps)

    forecast_index = pd.date_range(start=df.index[-1] + pd.Timedelta(days=1), periods=steps)
    forecast_df = pd.DataFrame({'forecast': forecast}, index=forecast_index)

    logger.info(f"Forecasting complete for {steps} steps ahead.")
    return forecast_df