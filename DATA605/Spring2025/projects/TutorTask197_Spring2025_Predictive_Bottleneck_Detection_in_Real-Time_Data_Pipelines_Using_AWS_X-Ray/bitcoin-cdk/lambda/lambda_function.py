import base64
import json
import boto3
import uuid
import os
from datetime import datetime
from decimal import Decimal 

# Set up clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

# Constants
table = dynamodb.Table(os.environ['TABLE_NAME'])
bucket_name = os.environ['BUCKET_NAME']

def lambda_handler(event, context):
    for record in event['Records']:
        # Decode the base64-encoded Kinesis data
        payload = base64.b64decode(record['kinesis']['data']).decode('utf-8')
        data = json.loads(payload)

        # Extract Bitcoin price
        price = data.get('price_usd', 0)

        # Process only if price is above $80,000
        if price > 80000:
            data['flag'] = 'High Price'
            data['processed_at'] = datetime.utcnow().isoformat()

            # Aggregation fix with Decimal
            agg_id = 'btc_high_avg'
            response = table.get_item(Key={'id': agg_id})
            item = response.get('Item', {'id': agg_id, 'count': 0, 'total': Decimal('0.0')})

            new_count = item['count'] + 1
            new_total = item['total'] + Decimal(str(price))
            new_avg = new_total / new_count

            table.put_item(Item={
                'id': agg_id,
                'count': new_count,
                'total': new_total,
                'average': new_avg
            })

            # Store in S3
            file_key = f"bitcoin-records/{uuid.uuid4()}.json"
            s3.put_object(
                Bucket=bucket_name,
                Key=file_key,
                Body=json.dumps(data),
                ContentType='application/json'
            )

            print(f"📦 Stored in S3: {file_key}")
            print(f"📊 Updated avg (high only): ${round(float(new_avg), 2)} after {new_count} records")
        else:
            print(f" Skipped price: ${price}")

    return {
        'statusCode': 200,
        'body': 'Processed successfully'
    }
