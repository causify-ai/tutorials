from opensearchpy import OpenSearch, helpers
import pandas as pd
import json
import os

# Live data path
data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'bitcoin_prices.json')

# Elasticsearch setup
client = OpenSearch(
    [{'host': 'localhost', 'port': 9200}],
    use_ssl=False
)

index_name = 'bitcoin-prices'

# Create index if it doesn't exist
if not client.indices.exists(index_name):
    mapping = {
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "price": {"type": "float"},
                "pct_change": {"type": "float"}
            }
        }
    }
    client.indices.create(index=index_name, body=mapping)
    print(f"Created index `{index_name}`")

# Read live data
df = pd.read_json(data_path, lines=True)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df = df.sort_values('timestamp')
df['pct_change'] = df['price'].pct_change() * 100
df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S')

# Fetch existing timestamps from Elasticsearch (only recent ones)
query = {
    "size": 10000,
    "_source": ["timestamp"],
    "query": {"match_all": {}}
}
response = client.search(index=index_name, body=query)
existing_timestamps = set(hit['_source']['timestamp'] for hit in response['hits']['hits'])

# Prepare new actions with pct_change
new_actions = [
    {
        "_index": index_name,
        "_source": {
            "timestamp": row['timestamp'],
            "price": row['price'],
            "pct_change": row['pct_change']
        }
    }
    for _, row in df.iterrows()
    if row['timestamp'] not in existing_timestamps
]

# Bulk insert only new
if new_actions:
    success, _ = helpers.bulk(client, new_actions)
    print(f"Ingested {success} new records into `{index_name}`.")
else:
    print("No new records to ingest.")
