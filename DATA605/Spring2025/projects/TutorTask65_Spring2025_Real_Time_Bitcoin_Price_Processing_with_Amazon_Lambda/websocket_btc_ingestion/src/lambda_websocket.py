import json
import boto3
import datetime
import websocket
import threading

S3_BUCKET = "ruthvick-btc-bucket"
S3_PREFIX = "websocket_btc_data/"

s3 = boto3.client("s3")

def on_message(ws, message):
    try:
        msg = json.loads(message)
        if msg.get("type") == "ticker":
            price = float(msg["price"])
            timestamp = datetime.datetime.utcnow().isoformat()
            data = {
                "timestamp": timestamp,
                "price_usd_per_btc": price
            }

            key = f"{S3_PREFIX}btc_ws_price_{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S')}.json"
            s3.put_object(
                Bucket=S3_BUCKET,
                Key=key,
                Body=json.dumps(data),
                ContentType="application/json"
            )
            print(f"[INFO] Uploaded: s3://{S3_BUCKET}/{key}")
    except Exception as e:
        print(f"[ERROR] {e}")

def on_error(ws, error):
    print(f"[WEBSOCKET ERROR] {error}")

def on_close(ws, close_status_code, close_msg):
    print("[WEBSOCKET CLOSED]")

def on_open(ws):
    subscribe_msg = {
        "type": "subscribe",
        "product_ids": ["BTC-USD"],
        "channels": ["ticker"]
    }
    ws.send(json.dumps(subscribe_msg))

def run_websocket():
    ws = websocket.WebSocketApp(
        "wss://ws-feed.exchange.coinbase.com",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )
    ws.run_forever()

# Lambda entry point
def lambda_handler(event, context):
    thread = threading.Thread(target=run_websocket)
    thread.start()

    # Let it run for 15 seconds (or any short duration)
    thread.join(timeout=15)
    return {
        "statusCode": 200,
        "body": json.dumps("WebSocket BTC ingestion triggered.")
    }
