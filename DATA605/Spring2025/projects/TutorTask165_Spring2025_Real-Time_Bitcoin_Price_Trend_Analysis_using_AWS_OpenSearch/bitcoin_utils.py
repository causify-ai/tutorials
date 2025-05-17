import os
import json
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pycoingecko import CoinGeckoAPI
from opensearchpy import OpenSearch, helpers
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Load environment variables
#load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

# Constants and paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, 'data')
RESULTS_DIR = os.path.join(ROOT_DIR, 'results')
BITCOIN_FILE = os.path.join(DATA_DIR, 'bitcoin_prices.json')
NEWS_FILE = os.path.join(DATA_DIR, 'crypto_news.json')
API_KEY = os.getenv("CRYPTO_PANIC_API_KEY")

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

def fetch_live_bitcoin_price():
    cg = CoinGeckoAPI()
    print("Starting live price fetch. Press Ctrl+C to stop.")
    try:
        while True:
            price_data = cg.get_price(ids='bitcoin', vs_currencies='usd')
            price = price_data['bitcoin']['usd']
            timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
            record = {"timestamp": timestamp, "price": price}
            with open(BITCOIN_FILE, 'a') as f:
                f.write(json.dumps(record) + '\n')
            print(f"[{timestamp}]  BTC Price: ${price}")
            time.sleep(45)
    except KeyboardInterrupt:
        print("\nStopped live fetching by user.")

def ingest_prices_to_opensearch():
    client = OpenSearch([{'host': 'localhost', 'port': 9200}], use_ssl=False)
    index_name = 'bitcoin-prices'

    if not client.indices.exists(index_name):
        mapping = {
            "mappings": {
                "properties": {
                    "timestamp": {"type": "date"},
                    "price": {"type": "float"},
                    "pct_change": {"type": "float"}
                }
            }
        }
        client.indices.create(index=index_name, body=mapping)

    df = pd.read_json(BITCOIN_FILE, lines=True)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    df['pct_change'] = df['price'].pct_change() * 100
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S')

    query = {"size": 10000, "_source": ["timestamp"], "query": {"match_all": {}}}
    response = client.search(index=index_name, body=query)
    existing = set(hit['_source']['timestamp'] for hit in response['hits']['hits'])

    new_actions = [
        {"_index": index_name, "_source": row.dropna().to_dict()}
        for _, row in df.iterrows() if row['timestamp'] not in existing
    ]

    if new_actions:
        success, _ = helpers.bulk(client, new_actions)
        print(f"Ingested {success} new records into `{index_name}`.")
    else:
        print("No new records to ingest.")

def scrape_crypto_news():
    url = 'https://cryptopanic.com/api/v1/posts/'
    params = {
        'auth_token': API_KEY,
        'currencies': 'BTC',
        'kind': 'news',
        'public': 'true'
    }

    print("Live news scraping started (Ctrl+C to stop)...")
    seen_urls = set()
    try:
        while True:
            res = requests.get(url, params=params)
            if res.status_code != 200:
                print("Error fetching news")
                time.sleep(60)
                continue
            data = res.json()
            count = 0
            for post in data.get('results', []):
                if post['url'] in seen_urls:
                    continue
                seen_urls.add(post['url'])
                record = {
                    'title': post['title'],
                    'url': post['url'],
                    'timestamp': post['published_at'],
                    'source': 'CryptoPanic'
                }
                with open(NEWS_FILE, 'a') as f:
                    f.write(json.dumps(record) + '\n')
                print(f"[NEWS] {record['timestamp']} - {record['title']}")
                count += 1
            print(f"Fetched {count} new articles.")
            time.sleep(30)
    except KeyboardInterrupt:
        print("\nNews scraping stopped.")

def embed_and_ingest_semantic_news():
    with open(NEWS_FILE) as f:
        news_articles = [json.loads(line) for line in f]

    model = SentenceTransformer('all-MiniLM-L6-v2')
    print(f"Embedding {len(news_articles)} articles...")
    texts = [article['title'] for article in news_articles]
    embeddings = model.encode(texts, show_progress_bar=True)

    client = OpenSearch([{'host': 'localhost', 'port': 9200}], use_ssl=False)
    index_name = 'crypto-news-semantic'

    if client.indices.exists(index_name):
        client.indices.delete(index=index_name)

    index_body = {
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                "url": {"type": "keyword"},
                "timestamp": {"type": "date"},
                "embedding": {"type": "dense_vector", "dims": 384}
            }
        }
    }
    client.indices.create(index=index_name, body=index_body)

    actions = [
        {
            "_index": index_name,
            "_source": {
                "title": article['title'],
                "url": article['url'],
                "timestamp": article['timestamp'],
                "embedding": emb.tolist()
            }
        }
        for article, emb in zip(news_articles, embeddings)
    ]

    helpers.bulk(client, actions)
    print(f"Successfully indexed {len(actions)} semantic news articles into `{index_name}`.")
