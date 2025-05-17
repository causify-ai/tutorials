# scripts/embed_and_ingest_semantic_news.py

from sentence_transformers import SentenceTransformer
from opensearchpy import OpenSearch, helpers
import json, os
from tqdm import tqdm

# Load local news JSON
news_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'crypto_news.json')
with open(news_path) as f:
    news_articles = [json.loads(line) for line in f]

# Load embedding model
print(" Loading embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings
print(f" Embedding {len(news_articles)} articles...")
texts = [article['title'] for article in news_articles]
embeddings = model.encode(texts, show_progress_bar=True)

# Connect to OpenSearch
client = OpenSearch([{'host': 'localhost', 'port': 9200}], use_ssl=False)
index_name = 'crypto-news-semantic'

# Create index with dense_vector mapping
if client.indices.exists(index_name):
    client.indices.delete(index=index_name)

index_body = {
    "mappings": {
        "properties": {
            "title": {"type": "text"},
            "url": {"type": "keyword"},
            "timestamp": {"type": "date"},
            "embedding": {
                "type": "dense_vector",
                "dims": 384  # match all-MiniLM-L6-v2
            }
        }
    }
}
client.indices.create(index=index_name, body=index_body)

# Prepare and bulk ingest
print("Ingesting into OpenSearch...")
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
print(f" Successfully indexed {len(actions)} semantic news articles into `{index_name}`.")
