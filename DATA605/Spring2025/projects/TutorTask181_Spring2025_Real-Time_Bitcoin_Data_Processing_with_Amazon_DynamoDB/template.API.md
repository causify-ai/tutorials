# Interacting with DynamoDB via Boto3 (Python API)

This project uses **Amazon DynamoDB** as a storage backend for Bitcoin price data. We leverage **Boto3**, the AWS SDK for Python, to connect to DynamoDB, insert new price records, and retrieve historical data.

---

## Connecting to DynamoDB

```python
import boto3

# Initialize DynamoDB resource (uses default AWS credentials & region)
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Reference the specific table
table = dynamodb.Table('BitcoinPrices')

#Writing Data to DynamoDB (PutItem)

import time
import requests

# Fetch current Bitcoin price from CoinGecko API
api_url = "https://api.coingecko.com/api/v3/simple/price"
params = {"ids": "bitcoin", "vs_currencies": "usd"}
response = requests.get(api_url, params=params).json()
current_price = response["bitcoin"]["usd"]

# Prepare item with current timestamp and price
timestamp = int(time.time())
item = {"timestamp": timestamp, "price": float(current_price)}

# Store the item in DynamoDB
table.put_item(Item=item)
print(f"Inserted price ${current_price} at timestamp {timestamp}")


# Retrieving a Single Item (GetItem)

# Retrieve a specific item by primary key
key = {"timestamp": timestamp}
result = table.get_item(Key=key)

if "Item" in result:
    item = result["Item"]
    print(f"Retrieved price ${item['price']} at timestamp {item['timestamp']}")
else:
    print("Item not found!")

# Scanning Multiple Items (Scan)

# Retrieve all items from the table
scan_response = table.scan()
items = scan_response.get('Items', [])
print(f"Retrieved {len(items)} items from DynamoDB")

