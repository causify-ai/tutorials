import boto3
import os

BUCKET_NAME = 'btc-batch-data-ganesh'
FILE_NAME = 'btc_price_plot.png'
S3_KEY = 'charts/' + FILE_NAME #saves inside charts/ folder in S3

def upload_plot():
    if not os.path.exists(FILE_NAME):
        print(f"Plot file '{FILE_NAME}' not found.")
        return

    s3 = boto3.client('s3')
    try:
        s3.upload_file(FILE_NAME, BUCKET_NAME, S3_KEY)
        print(f"Uploaded plot to s3 as '{S3_KEY}'")
    except Exception as e:
        print("Upload failed:", e)

if __name__ == "__main__":
    upload_plot()