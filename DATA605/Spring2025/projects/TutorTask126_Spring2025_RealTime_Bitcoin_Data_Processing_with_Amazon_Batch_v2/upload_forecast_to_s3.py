import boto3
import os

BUCKET_NAME = 'btc-batch-data-ganesh'
FILE_NAME = 'btc_forecast_plot.png'
S3_KEY = 'charts/' + FILE_NAME

def upload_forecast_plot():
    if not os.path.exists(FILE_NAME):
        print(f"File '{FILE_NAME}' not found.")
        return
    
    s3 = boto3.client('s3')
    try:
        s3.upload_file(FILE_NAME, BUCKET_NAME, S3_KEY)
        print(f"Uploaded forecast plot to S3 as '{S3_KEY}' ")
    except Exception as e:
        print("Upload failed:, e")

if __name__ == "__main__":
    upload_forecast_plot()
