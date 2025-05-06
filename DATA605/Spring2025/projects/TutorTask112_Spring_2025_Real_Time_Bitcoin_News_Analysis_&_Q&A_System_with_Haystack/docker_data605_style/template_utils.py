# template_utils.py
import re
from typing import List
from transformers import pipeline

# Sentiment Analysis Pipeline
sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def clean_text(text: str) -> str:
    """
    Removes URLs, special characters, and excessive whitespace from the input text.
    """
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def chunk_paragraphs(text: str, chunk_size: int = 500) -> List[str]:
    """
    Splits long text into smaller chunks for processing.
    """
    words = text.split()
    return [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

def score_sentiment(text: str) -> str:
    """
    Returns sentiment label (POSITIVE/NEGATIVE) for the given text.
    """
    result = sentiment_pipeline(text[:512])  # truncate to avoid model limits
    return result[0]['label']
