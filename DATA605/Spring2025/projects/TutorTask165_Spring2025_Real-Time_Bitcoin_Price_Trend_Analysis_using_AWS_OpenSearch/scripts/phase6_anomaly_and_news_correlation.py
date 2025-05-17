import pandas as pd
import json, os
from opensearchpy import OpenSearch
from datetime import timedelta
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Load price data
price_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'bitcoin_prices.json')
df = pd.read_json(price_path, lines=True)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['pct_change'] = df['price'].pct_change() * 100

# Detect anomalies (e.g., > ±2% change)
anomalies = df[abs(df['pct_change']) > 2]
# top_anomalies = df.nlargest(30, 'pct_change')  # Top 30 increases
# bottom_anomalies = df.nsmallest(30, 'pct_change')  # Top 30 decreases
# anomalies = pd.concat([top_anomalies, bottom_anomalies])

print(f"Detected {len(anomalies)} anomalies.")

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Connect to OpenSearch
client = OpenSearch([{"host": "localhost", "port": 9200}], use_ssl=False)

# For each anomaly, fetch top 3 related news articles
results = []
for _, row in tqdm(anomalies.iterrows(), total=len(anomalies)):
    date = row['timestamp']
    window_start = (date - timedelta(days=1)).isoformat()
    window_end = (date + timedelta(days=1)).isoformat()

    # Fetch recent news
    query = {
        "query": {
            "range": {
                "timestamp": {
                    "gte": window_start,
                    "lte": window_end
                }
            }
        }
    }
    response = client.search(index="crypto-news", body=query, size=20)
    articles = response['hits']['hits']

    # If semantic index exists, use vector search
    if client.indices.exists("crypto-news-semantic"):
        q_vec = model.encode(row['timestamp'].isoformat()[:10] + " bitcoin movement").tolist()
        sem_query = {
            "size": 3,
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": q_vec}
                    }
                }
            }
        }
        sem_res = client.search(index="crypto-news-semantic", body=sem_query)
        sem_articles = [hit['_source']['title'] for hit in sem_res['hits']['hits']]
    else:
        sem_articles = [a['_source']['title'] for a in articles[:3]]

    results.append({
        "timestamp": row['timestamp'].isoformat(),
        "pct_change": row['pct_change'],
        "top_news": sem_articles
    })

# Save report
os.makedirs("../results", exist_ok=True)
with open("../results/anomaly_correlation_report.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nCorrelation report saved to results/anomaly_correlation_report.json")

