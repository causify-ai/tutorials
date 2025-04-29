import requests
import pandas as pd
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
from datetime import datetime

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

# CryptoPanic API key
api_key = '223fbd8f4a8ebc21443ef868d1e95e0fc44cc5b0'  # <<< Put your key here

# Fetch Bitcoin news
url = f"https://cryptopanic.com/api/v1/posts/?auth_token=223fbd8f4a8ebc21443ef868d1e95e0fc44cc5b0&currencies=BTC,ETH"
response = requests.get(url)
data = response.json()

# Process and insert news into OpenSearch
if 'results' in data:
    for article in data['results']:
        news_doc = {
            'published_at': article.get('published_at', datetime.utcnow().isoformat()),
            'title': article.get('title', 'No Title'),
            'url': article.get('url', ''),
            'source': article.get('source', {}).get('title', 'Unknown Source')
        }
        
        # Insert into OpenSearch
        response = client.index(
            index="bitcoin-news",
            body=news_doc
        )
        
        print(f"Indexed news article: {news_doc['title']}")
else:
    print("No news found or API limit reached.")
