import requests
import re
from haystack.schema import Document
from haystack.nodes import PreProcessor
from config import CRYPTOPANIC_API_KEY

# ----------------------------------------
# Initialize Sentiment Analyzer
# ----------------------------------------
from transformers import pipeline

# Option 1: General-purpose sentiment model (default)
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english"
)

# Option 2: Financial sentiment model (uncomment to use)
# sentiment_analyzer = pipeline(
#     "sentiment-analysis",
#     model="ProsusAI/finbert"
# )


def fetch_crypto_news(api_token=CRYPTOPANIC_API_KEY, currency="BTC", filter="news"):
    """
    Fetch Bitcoin-related news articles using the CryptoPanic API.

    Returns:
        List[Dict]: A list of parsed news article metadata.
    """
    url = f"https://cryptopanic.com/api/v1/posts/?auth_token={api_token}&currencies={currency}&filter={filter}"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json().get("results", [])
    return [
        {
            "title": item.get("title", ""),
            "content": item.get("url", ""),
            "published_at": item.get("published_at", ""),
            "source": item.get("domain", "unknown")
        }
        for item in data
    ]


def create_documents(news_data):
    """
    Convert raw news dictionaries into Haystack Document objects.
    """
    return [
        Document(
            content=f"{item['title']} - {item['content']}",
            meta={"source": item["source"]}
        )
        for item in news_data
    ]


def split_documents(documents):
    """
    Split longer documents into chunks for better retrieval.
    """
    preprocessor = PreProcessor(
        split_length=100,
        split_overlap=20,
        clean_empty_lines=True,
        clean_whitespace=True,
        split_respect_sentence_boundary=True
    )
    return preprocessor.process(documents)


def clean_text(text):
    """
    Clean input text by removing URLs, special symbols, and extra whitespace.

    Parameters:
        text (str): Raw input text

    Returns:
        str: Cleaned, plain text suitable for sentiment analysis
    """
    text = re.sub(r"http\S+", "", text)  # Remove URLs
    text = re.sub(r"[^A-Za-z0-9\s.,!?]", "", text)  # Remove special characters like $, @
    return text.strip()


def analyze_sentiment(text):
    """
    Analyze sentiment of cleaned input text using a transformer model.

    Parameters:
        text (str): Input text to analyze

    Returns:
        Tuple[str, float]: Sentiment label and confidence score
    """
    cleaned = clean_text(text[:512])
    if not cleaned:
        return "NEUTRAL", 0.0
    result = sentiment_analyzer(cleaned)[0]
    return result["label"], result["score"]
