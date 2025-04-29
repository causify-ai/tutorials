from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3
from pycoingecko import CoinGeckoAPI
from datetime import datetime
import time

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

# Initialize CoinGecko API
cg = CoinGeckoAPI()

# 📢 Start infinite loop
while True:
    try:
        # Fetch Bitcoin price
        price_info = cg.get_price(ids='bitcoin', vs_currencies='usd')
        print("Fetched price info:", price_info)

        # Prepare document
        doc = {
            'timestamp': datetime.utcnow().isoformat(),
            'price_usd': price_info['bitcoin']['usd']
        }

        # Index into OpenSearch
        response = client.index(
            index="bitcoin-prices",
            body=doc
        )

        print("Indexed document:", response)

    except Exception as e:
        print("Error occurred:", e)
        
    time.sleep(60)
