Real-Time Bitcoin Price Processing with AWS Lambda
This project fetches live Bitcoin prices from the Coinbase API and uploads the data to Amazon S3 using an AWS Lambda function triggered every minute via EventBridge.

Current Features
Live BTC price fetched via HTTP request (requests)

Uploaded to S3 in JSON format with a timestamp

Lambda triggered by EventBridge every 1 minute

Local script version runs live for 2 minutes, fetching every 15 seconds

Folder Structure

TutorTask65_Real_Time_BTC_Price_Processing/
├── ingest/                # Local test script
├── utils/                 # Shared logic (price fetch & S3 upload)
├── aws_lambda_package/    # Lambda deployment code & dependencies
├── notebooks/             # Main notebook
├── README.md
Note: The 2-minute fetch loop is implemented only locally, not in the deployed Lambda yet.