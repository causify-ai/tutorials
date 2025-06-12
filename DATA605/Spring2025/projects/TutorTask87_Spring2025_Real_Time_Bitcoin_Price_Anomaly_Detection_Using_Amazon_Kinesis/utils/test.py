from utils import fetch_bitcoin_price, send_to_kinesis

btc_data = fetch_bitcoin_price()
response = send_to_kinesis("bitcoin-price-stream", "us-east-1", btc_data)

print("✅ Data sent! Response from Kinesis:")
print(response)
