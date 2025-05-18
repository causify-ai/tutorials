Real-Time Bitcoin Price Analysis Pipeline

Overview

This project implements a fully automated, end-to-end pipeline on AWS to ingest, process, and analyze real-time Bitcoin price data. It integrates machine learning to predict short-term price movements and provides instant alerts and an interactive dashboard for visualization.

Key Features:

Continuous Ingestion: Fetches live BTC/USD prices every minute via the CoinGecko API.

Stream Processing: Uses Amazon Kinesis and AWS Lambda to compute technical indicators (SMA, RSI), detect anomalies, and generate buy/sell signals.

Alerting: Publishes instant email notifications via Amazon SNS when trading signals or large price swings occur.

Machine Learning: Trains an LSTM model in SageMaker (using Spot Instances) on historical data stored in S3, with daily automated retraining triggered by CloudWatch Events.

Real-Time Inference: Hosts the trained model as a SageMaker endpoint (BitcoinPricePredictor) for low-latency next-minute forecasts.

Interactive Dashboard: Provides a Streamlit app that visualizes current prices and forecasts, with user-tunable controls and auto-refresh.

Infrastructure as Code: All AWS resources are defined and managed through a single CloudFormation template for repeatable deployments and clean teardown.

Architecture

CloudFormation Template deploys:

Amazon Kinesis Data Stream

S3 buckets for raw data and model artifacts

SNS topic for alerts

IAM roles and policies

AWS Lambda functions (processor and retrainer)

EventSourceMapping (Kinesis → Lambda)

Data Ingestion: Python scraper writes prices into Kinesis every minute.

Processing Lambda: Calculates SMA, RSI, detects anomalies, appends raw data to S3, and publishes alerts to SNS.

Automated Retraining: CloudWatch Events invokes retrain Lambda daily, which starts a SageMaker training job on the S3 CSV.

Model Hosting: SageMaker deploys the latest LSTM model as a real-time HTTPS endpoint.

Dashboard: Streamlit app reads history from S3, fetches live prices, calls the endpoint for next-minute forecasts, and renders interactive charts.

Prerequisites

AWS account with permissions for CloudFormation, Kinesis, Lambda, S3, SNS, CloudWatch, SageMaker.

AWS CLI configured or use IAM role in SageMaker Studio/Notebook Instance.

Python 3.7+ with boto3, pycoingecko, pandas, numpy, streamlit, sagemaker, and related libraries.

Setup & Deployment

Provision Infrastructure

aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name BitcoinPipelineStack \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides EnvName=prod

Upload Historical Data

aws s3 cp bitcoin_prices.csv s3://<RawBucket>/bitcoin_prices.csv

Train Initial Model (Notebook cell)

Configure and run the SageMaker TensorFlow estimator to fit train.py on the S3 CSV.

Deploy Inference Endpoint (Notebook cell)

Call estimator.deploy(...) to create BitcoinPricePredictor.

Package & Deploy Retrain Lambda (Notebook cell)

Zip and create BitcoinRetrainFunction, passing S3 bucket names and hyperparameters.

Schedule Daily Retraining (Notebook cell)

Create a CloudWatch Events rule and target the retrain Lambda.

Running the Dashboard

Install dependencies

pip install streamlit streamlit-autorefresh pycoingecko boto3 pandas numpy sagemaker plotly

Set environment variable

export RAW_BUCKET=<your-raw-bucket-name>

Launch Streamlit

streamlit run dashboard.py --server.headless true --server.address 0.0.0.0 --server.port 8501

Access the UI
Open in your browser or via Jupyter proxy:
https://<your-notebook-domain>/proxy/8501/





