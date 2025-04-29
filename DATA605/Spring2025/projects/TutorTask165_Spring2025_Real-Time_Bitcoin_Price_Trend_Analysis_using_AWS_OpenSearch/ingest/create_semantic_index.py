from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3

# Connect to OpenSearch
region = 'us-east-2'
service = 'es'
credentials = boto3.Session().get_credentials()

awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'search-bitcoin-price-opensearch-t4nnkxsbs5blzuwcyme6z5czqi.us-east-2.es.amazonaws.com'  # replace
port = 443

client = OpenSearch(
    hosts=[{'host': host, 'port': port}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# Define k-NN enabled mapping
mapping = {
  "settings": {
    "index.knn": True
  },
  "mappings": {
    "properties": {
      "title": {"type": "text"},
      "url": {"type": "keyword"},
      "published_at": {"type": "date"},
      "embedding": {
        "type": "knn_vector",
        "dimension": 384  # MiniLM embedding size
      }
    }
  }
}

# Create new index
response = client.indices.create(index='bitcoin-news-semantic', body=mapping)
print(response)
