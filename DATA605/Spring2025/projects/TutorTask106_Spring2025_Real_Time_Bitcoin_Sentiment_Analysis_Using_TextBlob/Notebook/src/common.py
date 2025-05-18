from src.logger import get_logger
from pycoingecko import CoinGeckoAPI
from newsapi import NewsApiClient
import os

logger = get_logger(__name__)

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
if not NEWS_API_KEY:
    logger.warning("NEWS_API_KEY not set in environment variables")
# RELEVANT_SOURCES = [
#     # 'australian-financial-review',
#     'bloomberg',
#     'business-insider',
#     # 'financial-post',
#     'fortune',
#     # 'the-wall-street-journal'
# ]
newsapi = NewsApiClient(api_key=NEWS_API_KEY) if NEWS_API_KEY else None
coingecko = CoinGeckoAPI()

BASE_SAVE_DIR = 'data'

# Dictionary with categorized stance
BITCOIN_STANCE = {
    "pro_bitcoin": [
        "australian-financial-review",
        "bloomberg",
        "business-insider",
        "fortune",
        "wirtschafts-woche"
    ],
    "neutral": [
        "the-wall-street-journal",
        "handelsblatt",
        "il-sole-24-ore",
        "les-echos"
    ],
    "against_bitcoin": [
        "argaam",
        "die-zeit",
        "financial-post"
    ]
}

# Initialize relevant sources list
RELEVANT_SOURCES = []

def set_relevant_sources(*categories):
    """
    Updates RELEVANT_SOURCES based on selected categories from BITCOIN_STANCE.

    Args:
        *categories: One or more keys from BITCOIN_STANCE to populate RELEVANT_SOURCES.
    """
    global RELEVANT_SOURCES
    RELEVANT_SOURCES = []

    for category in categories:
        if category in BITCOIN_STANCE:
            RELEVANT_SOURCES.extend(BITCOIN_STANCE[category])
        else:
            print(f"Warning: '{category}' is not a valid category.")

    # Remove duplicates if same source appears in multiple selected categories
    RELEVANT_SOURCES = list(set(RELEVANT_SOURCES))
    print(f"RELEVANT_SOURCES updated with categories {categories}:\n{RELEVANT_SOURCES}")


set_relevant_sources('pro_bitcoin')           # Only pro-bitcoin sources
# set_relevant_sources('pro_bitcoin', 'neutral')  # To include both pro and neutral