from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import pandas as pd

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

# Fetch Bitcoin price data
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

# Convert timestamp to datetime and sort
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp')

# Calculate % change
df['percent_change'] = df['price_usd'].pct_change() * 100

# Detect volatility: where absolute % change > 5%
volatility_threshold = 0.01  # you can adjust this if needed
volatility_events = df[df['percent_change'].abs() > volatility_threshold]

# Output
if not volatility_events.empty:
    print("Volatility Detected!")
    print(volatility_events[['timestamp', 'price_usd', 'percent_change']])
else:
    print("No significant volatility detected.")

