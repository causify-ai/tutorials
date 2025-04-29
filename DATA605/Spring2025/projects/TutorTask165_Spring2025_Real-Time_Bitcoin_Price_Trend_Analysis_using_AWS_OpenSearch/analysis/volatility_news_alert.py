from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
import pandas as pd
from sentence_transformers import SentenceTransformer

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

host = 'search-bitcoin-price-opensearch-t4nnkxsbs5blzuwcyme6z5czqi.us-east-2.es.amazonaws.com'  # <-- replace with your endpoint
port = 443

client = OpenSearch(
    hosts=[{'host': host, 'port': port}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# Load Bitcoin price data
query = {
  "size": 1000,
  "query": {
    "match_all": {}
  }
}

response = client.search(index="bitcoin-prices", body=query)
hits = response['hits']['hits']

# Build price DataFrame
data = []
for hit in hits:
    source = hit['_source']
    data.append(source)

df = pd.DataFrame(data)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp')

# Calculate % change
df['percent_change'] = df['price_usd'].pct_change() * 100

# Detect volatility (example: threshold 5%)
volatility_threshold = 0.01
volatility_events = df[df['percent_change'].abs() > volatility_threshold]

if not volatility_events.empty:
    print("Volatility detected!")

    # For each volatility event, search related news
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    for idx, row in volatility_events.iterrows():
        timestamp = row['timestamp']
        price = row['price_usd']
        change = row['percent_change']
        
        print(f"\n Volatility Event: {timestamp} | Price: ${price} | Change: {change:.2f}%")
        
        # Build smart query based on up/down
        if change > 0:
            query_text = "Bitcoin price surge news"
        else:
            query_text = "Bitcoin price crash news"
        
        # Create embedding
        query_embedding = model.encode(query_text).tolist()

        # Run semantic search on news index
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

        news_response = client.search(index="bitcoin-news-semantic", body=search_query)

        print("Related News Found:")
        for news_hit in news_response['hits']['hits']:
            news = news_hit['_source']
            print(f"- {news['title']} ({news['published_at']})")
            print(f"  URL: {news['url']}")
else:
    print("No major volatility detected today.")
