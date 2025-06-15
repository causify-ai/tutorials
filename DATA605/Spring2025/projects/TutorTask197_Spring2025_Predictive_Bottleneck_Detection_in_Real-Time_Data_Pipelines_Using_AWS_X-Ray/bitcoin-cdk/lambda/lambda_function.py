import json
import base64
import boto3
import uuid
import os
import time
from datetime import datetime
from decimal import Decimal
from aws_xray_sdk.core import patch_all, xray_recorder
patch_all()

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

bucket_name = os.environ['BUCKET_NAME']
table_name = os.environ['TABLE_NAME']
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    for record in event['Records']:
        start_time = time.time()

        # Decode and parse
        payload = base64.b64decode(record['kinesis']['data']).decode('utf-8')
        data = json.loads(payload)

        price = data.get('price_usd', 0)
        timestamp = data.get('timestamp', int(time.time()))
        hour_dt = datetime.utcfromtimestamp(timestamp).replace(minute=0, second=0, microsecond=0)
        hour_str = hour_dt.isoformat()

        # Flag price levels
        if price > 100000:
            flag = '🚨 Extremely High Price'
        elif price > 65000:
            flag = '⚠️ High Price'
        elif price < 30000:
            flag = '🪙 Low Price'
        else:
            flag = '✅ Average Price'
        
        data['flag'] = flag
        data['processed_at'] = datetime.utcnow().isoformat()

        # Store flagged record to S3
        file_key = f"bitcoin-records/{uuid.uuid4()}.json"
        s3.put_object(
            Bucket=bucket_name,
            Key=file_key,
            Body=json.dumps(data),
            ContentType='application/json'
        )
        print(f"📦 Stored in S3: {file_key}")

        # Update hourly metrics in DynamoDB
        response = table.get_item(Key={'id': hour_str})
        item = response.get('Item', {
            'id': hour_str,
            'count': 0,
            'total': Decimal('0'),
            'max': Decimal(str(price)),
            'min': Decimal(str(price)),
            'total_latency': Decimal('0'),
            'max_latency': Decimal('0'),
            'min_latency': Decimal('1000000'),
            'error_count': 0,
            'flag_counts': {}
        })

        item['count'] += 1
        item['total'] += Decimal(str(price))
        item['max'] = max(item['max'], Decimal(str(price)))
        item['min'] = min(item['min'], Decimal(str(price)))
        item['average'] = item['total'] / item['count']

        # Processing time
        end_time = time.time()
        processing_time = round((end_time - start_time) * 1000, 2)
        item['total_latency'] += Decimal(str(processing_time))
        item['max_latency'] = max(item['max_latency'], Decimal(str(processing_time)))
        item['min_latency'] = min(item['min_latency'], Decimal(str(processing_time)))
        item['avg_latency'] = item['total_latency'] / item['count']

      
        # X-Ray annotations

        with xray_recorder.in_subsegment('processing') as subsegment:
            subsegment.put_annotation("flag", flag)
            subsegment.put_annotation("price_usd", round(price, 2))
            subsegment.put_annotation("data_volume_bytes", len(json.dumps(data).encode("utf-8")))
            subsegment.put_annotation("shard_id", record['kinesis']['partitionKey'])
            subsegment.put_annotation("processing_time_ms", processing_time)
            subsegment.put_annotation("hour_str", hour_str)
            subsegment.put_annotation("error", False)


        # Flag count update
        if flag in item['flag_counts']:
            item['flag_counts'][flag] += 1
        else:
            item['flag_counts'][flag] = 1

        table.put_item(Item=item)
        print(f"📊 Updated metrics for {hour_str} | Flag: {flag} | Latency: {processing_time} ms")

    return {'statusCode': 200}
