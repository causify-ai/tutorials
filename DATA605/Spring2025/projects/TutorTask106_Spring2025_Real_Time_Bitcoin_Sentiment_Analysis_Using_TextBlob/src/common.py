from src.logger import get_logger
from pycoingecko import CoinGeckoAPI
from newsapi import NewsApiClient
import os

logger = get_logger(__name__)

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
if not NEWS_API_KEY:
    logger.warning("NEWS_API_KEY not set in environment variables")
RELEVANT_SOURCES = [
    # 'australian-financial-review',
    'bloomberg',
    'business-insider',
    # 'financial-post',
    'fortune',
    # 'the-wall-street-journal'
]
newsapi = NewsApiClient(api_key=NEWS_API_KEY) if NEWS_API_KEY else None
coingecko = CoinGeckoAPI()