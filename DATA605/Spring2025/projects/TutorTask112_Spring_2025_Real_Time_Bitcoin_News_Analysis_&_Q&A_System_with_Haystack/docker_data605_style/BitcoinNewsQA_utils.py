import requests
from haystack.schema import Document
from haystack.nodes import PreProcessor
from config import CRYPTOPANIC_API_KEY

# -------------------------------
# Initialize Sentiment Analyzer
# -------------------------------
from transformers import pipeline

# Load Hugging Face sentiment-analysis pipeline once with a fixed model
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert/distilbert-base-uncased-finetuned-sst-2-english"
)


def fetch_crypto_news(api_token=CRYPTOPANIC_API_KEY, currency="BTC", filter="news"):
    """
    Fetch Bitcoin-related news articles using the CryptoPanic API.

    Parameters:
        api_token (str): API key for CryptoPanic.
        currency (str): Cryptocurrency symbol to filter news (default: "BTC").
        filter (str): Type of news (e.g., "news", "sentiment").

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

    Parameters:
        news_data (List[Dict]): News articles returned from fetch_crypto_news.

    Returns:
        List[Document]: A list of Haystack-compatible Document objects.
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

    Parameters:
        documents (List[Document]): Haystack Document objects.

    Returns:
        List[Document]: Chunked and preprocessed documents.
    """
    preprocessor = PreProcessor(
        split_length=100,
        split_overlap=20,
        clean_empty_lines=True,
        clean_whitespace=True,
        split_respect_sentence_boundary=True
    )
    return preprocessor.process(documents)


def analyze_sentiment(text):
    """
    Analyze sentiment of a given text using Hugging Face transformers.

    Parameters:
        text (str): Input text to analyze (e.g., context of an answer).

    Returns:
        Tuple[str, float]: Sentiment label (e.g., "POSITIVE") and score (confidence).
    """
    result = sentiment_analyzer(text[:512])[0]  # Limit to 512 characters
    return result['label'], result['score']
