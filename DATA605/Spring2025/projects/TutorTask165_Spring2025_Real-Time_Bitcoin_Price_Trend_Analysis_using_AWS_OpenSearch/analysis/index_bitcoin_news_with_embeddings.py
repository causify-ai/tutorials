from sentence_transformers import SentenceTransformer
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3

# OpenSearch connection
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

host = 'search-bitcoin-price-opensearch-t4nnkxsbs5blzuwcyme6z5czqi.us-east-2.es.amazonaws.com'  
port = 443

client = OpenSearch(
    hosts=[{'host': host, 'port': port}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# Fetch Bitcoin news from the old index
query = {
  "size": 1000,
  "query": {
    "match_all": {}
  }
}

response = client.search(index="bitcoin-news", body=query)
hits = response['hits']['hits']

# Initialize embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Process each news article
for hit in hits:
    news = hit['_source']
    title = news.get('title', '')

    # Generate embedding for title
    embedding = model.encode(title).tolist()

    # Prepare document for new semantic index
    doc = {
        "title": title,
        "url": news.get('url', ''),
        "published_at": news.get('published_at', ''),
        "embedding": embedding
    }

    # Index into semantic OpenSearch index
    response = client.index(index="bitcoin-news-semantic", body=doc)
    print(f"Indexed with embedding: {title}")
