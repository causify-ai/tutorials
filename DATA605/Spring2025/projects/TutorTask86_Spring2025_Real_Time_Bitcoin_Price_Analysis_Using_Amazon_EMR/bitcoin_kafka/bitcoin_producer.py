import requests, json, time
import boto3

s3 = boto3.client('s3')
bucket = 'bitcoin-price-streaming-data'
folder = 'data_v2/'

while True:
    try:
        response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
        data = response.json()

        if 'bitcoin' in data and 'usd' in data['bitcoin']:
            price = data['bitcoin']['usd']
            timestamp = int(time.time())
            message = {
                "timestamp": timestamp,
                "price": price
            }

            filename = f'{folder}{timestamp}.json'
            s3.put_object(Bucket=bucket, Key=filename, Body=json.dumps(message))
            print(f"✅ Uploaded to S3: {filename}", message)
        else:
            print("⚠️ Unexpected API response:", data)

    except Exception as e:
        print("❌ Error:", e)

    time.sleep(60)


