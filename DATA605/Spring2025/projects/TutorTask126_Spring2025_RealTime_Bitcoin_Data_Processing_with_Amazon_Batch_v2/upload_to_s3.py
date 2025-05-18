import boto3
import os

#s3 configuration
BUCKET_NAME = 'btc-batch-data-ganesh'
FILE_NAME = 'btc_prices_data.csv'
S3_KEY = 'btc_prices_data.csv' #name it'll have in S3

#upload file to S3
def upload_to_s3():
    if not os.path.exists(FILE_NAME):
        print(f"File '{FILE_NAME} not found.")
        return
    
    s3 = boto3.client('s3')

    try:
        s3.upload_file(FILE_NAME, BUCKET_NAME, S3_KEY)
        print(f"Uploaded '{FILE_NAME}' to S3 bucket '{BUCKET_NAME}' as '{S3_KEY}' ")
    except Exception as e:
        print("Upload Failed.", e)

if __name__ == "__main__":
    upload_to_s3()