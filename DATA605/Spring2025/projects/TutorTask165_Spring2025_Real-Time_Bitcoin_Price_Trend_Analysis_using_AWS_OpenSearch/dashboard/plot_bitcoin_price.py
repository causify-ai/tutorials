from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import pandas as pd
import matplotlib.pyplot as plt

# OpenSearch connection
region = 'us-east-2'
service = 'es'
credentials = boto3.Session().get_credentials()

awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'search-bitcoin-price-opensearch-t4nnkxsbs5blzuwcyme6z5czqi.us-east-2.es.amazonaws.com'  # your real endpoint
port = 443

client = OpenSearch(
    hosts=[{'host': host, 'port': port}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# Query Bitcoin price documents
query = {
  "size": 1000,
  "query": {
    "match_all": {}
  }
}

response = client.search(index="bitcoin-prices", body=query)
hits = response['hits']['hits']

# Prepare DataFrame
data = []
for hit in hits:
    source = hit['_source']
    data.append(source)

df = pd.DataFrame(data)

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp')

# Calculate Moving Average
df['moving_avg'] = df['price_usd'].rolling(window=5).mean()

# Plot
plt.figure(figsize=(12,6))

# Plot actual Bitcoin prices
plt.plot(df['timestamp'], df['price_usd'], label='Bitcoin Price', marker='o')

# Plot moving average line
plt.plot(df['timestamp'], df['moving_avg'], label='5-Point Moving Average', linestyle='--')

# Add labels, title, grid
plt.title('Bitcoin Price with Moving Average')
plt.xlabel('Time')
plt.ylabel('Price (USD)')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

plt.show()
