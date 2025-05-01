import json
import boto3
import datetime
import requests

def lambda_handler(event, context):
    # Fetch live BTC price
    url = "https://api.coinbase.com/v2/prices/spot?currency=USD"
    response = requests.get(url)
    data = response.json()
    price = float(data['data']['amount'])
    timestamp = datetime.datetime.utcnow().isoformat()

    btc_data = {
        'timestamp': timestamp,
        'price': price
    }

    # Upload to S3
    s3 = boto3.client('s3')
    bucket_name = "ruthvick-btc-bucket"  # your bucket
    key = f"btc_data/btc_price_{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S')}.json"

    s3.put_object(Bucket=bucket_name, Key=key, Body=json.dumps(btc_data))

    return {
        'statusCode': 200,
        'body': json.dumps('BTC price fetched and uploaded successfully!')
    }
if __name__ == "__main__":
    btc_data = get_live_btc_price()
    print("📈 Fetched BTC Price:", btc_data)

    s3_path = upload_to_s3(btc_data, bucket_name="ruthvick-btc-bucket", file_name="btc_data/btc_price_test.json")
    print("✅ Uploaded to", s3_path)

