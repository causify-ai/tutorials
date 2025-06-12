# Amazon DynamoDB API Documentation

## Overview
This document outlines the key DynamoDB API interactions used in this project to store and retrieve Bitcoin price data in real-time.

---

## **Create DynamoDB Table**
The DynamoDB table is created to store Bitcoin prices with a timestamp as the primary key.
```python
import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table_name = "BitcoinPrices"

# Create the table if it does not exist
table = dynamodb.create_table(
    TableName=table_name,
    KeySchema=[{'AttributeName': 'timestamp', 'KeyType': 'HASH'}],
    AttributeDefinitions=[{'AttributeName': 'timestamp', 'AttributeType': 'N'}],
    ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
)
table.wait_until_exists()

## **Insert Bitcoin Price Data**
Each Bitcoin price data point is inserted as a new record:
# Insert a new record into DynamoDB
table.put_item(Item={
    'timestamp': 1744575538,
    'price': 83637.0
})

## **Scan the Table**
To retrieve all stored Bitcoin prices:
response = table.scan()
items = response['Items']
print(items)
