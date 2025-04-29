from sentence_transformers import SentenceTransformer
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3

# Connect to OpenSearch
region = 'us-east-2'
service = 'es'
credentials = boto3.Session().get_credentials()

awsauth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    region,
    service,
    session_token=credentials.token
)

host = 'search-bitcoin-price-opensearch-t4nnkxsbs5blzuwcyme6z5czqi.us-east-2.es.amazonaws.com'  # replace
port = 443

client = OpenSearch(
    hosts=[{'host': host, 'port': port}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# Initialize model
model = SentenceTransformer('all-MiniLM-L6-v2')

# User query
query_text = "Bitcoin ETF approval"

# Encode query
query_embedding = model.encode(query_text).tolist()

# Run kNN search
search_query = {
  "size": 5,
  "query": {
    "knn": {
      "embedding": {
        "vector": query_embedding,
        "k": 5
      }
    }
  }
}

response = client.search(index="bitcoin-news-semantic", body=search_query)

# Show results
for hit in response['hits']['hits']:
    print(f"Title: {hit['_source']['title']}")
    print(f"URL: {hit['_source']['url']}")
    print("-----")
