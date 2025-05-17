from opensearchpy import OpenSearch, helpers
import json, os

client = OpenSearch([{'host': 'localhost', 'port': 9200}], use_ssl=False)
index_name = 'crypto-news'
news_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'crypto_news.json')

if not client.indices.exists(index_name):
    client.indices.create(index=index_name, body={
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "title": {"type": "text"},
                "url": {"type": "keyword"},
                "source": {"type": "keyword"}
            }
        }
    })

with open(news_path) as f:
    records = [json.loads(line) for line in f]

actions = [{"_index": index_name, "_source": r} for r in records]
helpers.bulk(client, actions)
print(f"Ingested {len(actions)} news articles into {index_name}")
