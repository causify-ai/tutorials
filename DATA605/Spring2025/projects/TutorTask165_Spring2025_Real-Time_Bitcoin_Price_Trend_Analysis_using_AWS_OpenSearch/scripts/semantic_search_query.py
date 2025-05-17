# scripts/semantic_search_query.py

from sentence_transformers import SentenceTransformer
from opensearchpy import OpenSearch
import numpy as np

# Load embedding model
print(" Loading model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Connect to OpenSearch
client = OpenSearch([{'host': 'localhost', 'port': 9200}], use_ssl=False)
index = 'crypto-news-semantic'

# User query
query_text = input(" Enter your semantic query: ")
embedding = model.encode([query_text])[0].tolist()

# Run KNN vector search
print(" Searching...")
query = {
    "size": 5,
    "query": {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                "params": {"query_vector": embedding}
            }
        }
    }
}


response = client.search(index=index, body=query)
print("\nTop Results:\n")
for hit in response['hits']['hits']:
    title = hit['_source']['title']
    score = hit['_score']
    url = hit['_source']['url']
    print(f"- [{score:.2f}] {title}\n {url}\n")
