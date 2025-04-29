from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import pandas as pd

# OpenSearch connection
region = 'us-east-2'
service = 'es'
credentials = boto3.Session().get_credentials()

awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'search-bitcoin-price-opensearch-t4nnkxsbs5blzuwcyme6z5czqi.us-east-2.es.amazonaws.com'  # update your endpoint
port = 443

client = OpenSearch(
    hosts=[{'host': host, 'port': port}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# Search all Bitcoin price documents
query = {
  "size": 1000,   # fetch up to 1000 documents
  "query": {
    "match_all": {}
  }
}

response = client.search(index="bitcoin-prices", body=query)

# Extract documents
hits = response['hits']['hits']

# Display results nicely
data = []
for hit in hits:
    source = hit['_source']
    data.append(source)

# Convert to pandas DataFrame
df = pd.DataFrame(data)

print(df)
