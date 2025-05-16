# template.example.py

import requests
import json
import time
from datetime import datetime
from template_utils import clean_text, score_sentiment

CRYPTO_PANIC_API_KEY = "your_cryptopanic_api_key"  # Replace with your key
API_URL = f"https://cryptopanic.com/api/v1/posts/?auth_token={CRYPTO_PANIC_API_KEY}&currencies=BTC&public=true"

def fetch_latest_news():
    """
    Fetch latest Bitcoin news from CryptoPanic API.
    Returns a list of articles with relevant metadata.
    """
    response = requests.get(API_URL)
    if response.status_code != 200:
        print("Error fetching data:", response.status_code)
        return []

    raw_data = response.json().get("results", [])
    articles = []

    for item in raw_data:
        title = item.get("title", "")
        published_at = item.get("published_at", "")
        source = item.get("domain", "")
        url = item.get("url", "")
        body = clean_text(title)
        sentiment = score_sentiment(body)

        articles.append({
            "content": body,
            "published": published_at,
            "source": source,
            "url": url,
            "sentiment": sentiment,
            "timestamp": datetime.utcnow().isoformat()
        })

    return articles

if __name__ == "__main__":
    news_data = fetch_latest_news()
    print(json.dumps(news_data, indent=2))
