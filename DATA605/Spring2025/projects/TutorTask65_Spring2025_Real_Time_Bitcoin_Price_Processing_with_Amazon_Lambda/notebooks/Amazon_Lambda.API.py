from amazon_lambda_utils import get_live_btc_price, upload_to_s3

def lambda_handler(event=None, context=None):
    """
    Simulated Lambda handler: fetch live BTC price and upload to S3.
    """

    # Fetch live BTC price
    btc_price_data = get_live_btc_price()
    print(f"📈 Fetched BTC Price: {btc_price_data}")

    # Upload to S3
    bucket_name = "ruthvick-btc-bucket"
    file_name = "btc_price_latest.json"

    upload_path = upload_to_s3(btc_price_data, bucket_name, file_name)
    print(f"✅ Uploaded to {upload_path}")

# This runs when executing file directly (locally)
if __name__ == "__main__":
    lambda_handler()
