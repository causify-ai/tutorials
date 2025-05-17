# Example: Fetching, Storing, and Analyzing Bitcoin Price Data

This example demonstrates how to:
1. Fetch the real-time price of Bitcoin using CoinGecko API.
2. Store the data in Amazon DynamoDB.
3. Retrieve the data and analyze it.

---

## Step 1: Fetch the Latest Bitcoin Price

```python
import requests

# CoinGecko API endpoint
url = "https://api.coingecko.com/api/v3/simple/price"
params = {"ids": "bitcoin", "vs_currencies": "usd"}

response = requests.get(url, params=params)
data = response.json()
btc_price = data["bitcoin"]["usd"]
print(f"Current Bitcoin price (USD): ${btc_price}")

# Step 2: Insert the Price Data into DynamoDB
import boto3, time

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('BitcoinPrices')

timestamp = int(time.time())
item = {"timestamp": timestamp, "price": float(btc_price)}

table.put_item(Item=item)
print(f"Stored BTC price ${btc_price} at time {timestamp} into DynamoDB.")

# Step 3: Retrieve Historical Price Data
import pandas as pd

# Scan the DynamoDB table to get all price records
response = table.scan()
items = response.get('Items', [])

# Convert to DataFrame
df = pd.DataFrame(items)
df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
df = df.sort_values('timestamp')
print(df.head())

# Step 4: Analyze and Visualize Data
import matplotlib.pyplot as plt

plt.figure(figsize=(8, 5))
plt.plot(df['datetime'], df['price'], label='BTC Price', marker='o')
plt.xlabel('Time')
plt.ylabel('Price (USD)')
plt.title('Bitcoin Price Over Time')
plt.grid(True)
plt.show()

