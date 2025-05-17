from opensearchpy import OpenSearch

client = OpenSearch([{"host": "localhost", "port": 9200}], use_ssl=False)

query_text = input("Enter search query (BM25): ")

query = {
    "query": {
        "match": {
            "title": query_text
        }
    }
}

response = client.search(index="crypto-news", body=query)
print("\nTop BM25 Matches:")
for hit in response['hits']['hits'][:5]:
    print(f"- {hit['_source']['title']}\n  ↪ {hit['_source']['url']}\n")

