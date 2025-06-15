# 🧠 Predictive Bottleneck Detection in Real-Time Data Pipelines Using AWS X-Ray


## 🚀 Project Overview


This project demonstrates how to build a real-time data pipeline for performance monitoring and predictive analysis using AWS services and time-series forecasting. 

It streams live Bitcoin price data from the CoinGecko API using Amazon Kinesis, processes it serverlessly with AWS Lambda, and stores key metrics in S3 and DynamoDB. The pipeline is instrumented with AWS X-Ray to trace every step—from ingestion to storage—capturing detailed metadata such as latency, data volume, and anomalies. 

This trace data is critical for identifying bottlenecks, diagnosing errors, and ensuring system reliability at scale. Using Prophet, the project forecasts future latency trends, which are visualized on a live Plotly Dash dashboard. Additionally, it triggers Amazon SNS alerts when predicted latency exceeds a critical threshold—enabling proactive system management in real-time environments. 

This end-to-end system empowers developers to not only monitor, but also predict and respond to operational issues before they impact performance.


### Key Components

- **🔄 Stream Ingestion:**  
  Ingest real-time Bitcoin price data from the [CoinGecko API](https://www.coingecko.com/en/api) using **Amazon Kinesis Data Streams**.

- **⚙️ Serverless Processing:**  
  Use **AWS Lambda** to:
  - Filter and aggregate data
  - Track metrics like latency and data volume
  - Detect anomalies in price behavior
  - Annotate trace data using **AWS X-Ray**

- **💾 Data Storage:**  
  - Store processed records in **Amazon S3** for long-term logging  
  - Maintain hourly metrics in **Amazon DynamoDB** for fast querying

- **📈 Forecasting:**  
  Predict system performance trends using **Prophet**, a time-series forecasting library.

- **📊 Visualization:**  
  Display real-time insights and forecasts using an interactive **Plotly Dash** dashboard.

- **🚨 Alerting:**  
  Trigger **Amazon SNS alerts** when predicted latency exceeds a critical threshold.

---
## 📁 Project Directory Structure
```

├── Dockerfile
├── run.sh
├── main.py                         # Main entrypoint (runs ingestion & dashboard)
├── README.md
├── requirements.txt
│
├── bitcoin-cdk/
│ ├── app.py                          # CDK app entrypoint
│ ├── bitcoin_cdk/
│ │   ├── bitcoin_cdk_stack.py        # Defines Kinesis, Lambda, S3, DynamoDB resources
│ │   └── sns_alert_stack.py          # Defines SNS topic and subscription
│ ├── lambda/
│ │   └── lambda_function.py          # Kinesis-triggered Lambda for processing & tracing
│
├── scripts/
│ ├── send_to_kinesis.py          # Sends real-time + historical Bitcoin price data to Kinesis
│ ├── analyze_traces.py           # Aggregates metrics and forecasts latency using Prophet
│ └── send_latency_alerts.py      # Triggers SNS alert on high predicted latency.
│
├── utils/
│ ├── fetch_bitcoin.py            # CoinGecko API interface for real-time and historical prices
│ ├── kinesis_client.py           # Boto3 client for Kinesis
│ ├── fectch_xray_trace_data.py   # Queries X-Ray and extracts annotated trace metadata
│
├── visualization/
│ ├── forecast_visualizer.py      # Plotly graph functions
│ ├── plotly_dashboard.py         # Dash app for real-time latency and anomaly visualization
│ └── init.py
│
│── aws_xray_example.ipynb        # Full E2E walkthrough as Jupyter notebook
│── aws_xray_api.ipynb            # Demonstrates API functionality + wrappers
│── aws_xray_example.md           # Tutorial + narrative for the example pipeline
│── aws_xray_api.md               # Documentation of the core API & SDK usage
```
---
## 🧰 Tech Stack

This project combines real-time data engineering, observability, and predictive analytics using the following technologies:

### ☁️ AWS Services
- **Amazon Kinesis** – Real-time streaming ingestion of Bitcoin price data.
- **AWS Lambda** – Serverless processing: filtering, anomaly detection, metric aggregation.
- **Amazon S3** – Storage for JSON logs of flagged price records.
- **Amazon DynamoDB** – Stores hourly aggregated metrics and latency statistics.
- **AWS X-Ray** – Distributed tracing and observability; records latency, errors, metadata.
- **Amazon SNS** – Sends alerts when predicted latency exceeds thresholds.

### 🐍 Python Libraries
- **boto3** – Python SDK for interacting with AWS services.
- **requests** – Fetches real-time and historical Bitcoin data from the CoinGecko API.
- **Prophet** – Time-series forecasting model used to predict system latency.
- **Plotly Dash** – Interactive web dashboard for real-time monitoring and visualization.
- **pandas / numpy** – Data transformation and analysis.
- **aws-xray-sdk** – Captures annotations and traces within Lambda functions.

### 🐳 DevOps & Containerization
- **Docker** – Containerized the full data pipeline, analysis, and dashboard.
- **AWS CDK (Python)** – Infrastructure as code for deploying Kinesis, Lambda, S3, DynamoDB, and IAM roles.

---

## ✨ Key Features & Functionality

This project demonstrates a full-stack, real-time data pipeline with built-in monitoring, forecasting, and alerting.

### 🔄 Real-Time Data Ingestion
- Fetches live Bitcoin prices from the CoinGecko API and updates every one hour
- Streams data into Amazon Kinesis Data Streams for high-throughput ingestion

### ⚙️ Serverless Processing
Uses AWS Lambda to:
- Classify prices (e.g., low, average, high, extreme)
- Compute latency, error rate, and data volume
- Store raw data in Amazon S3
- Aggregate hourly metrics in DynamoDB

### 🧠 Predictive Analytics
- Forecasts future bottlenecks and latency using Prophet model
- Supports both hourly and daily latency prediction models

### 🛰️ Observability with AWS X-Ray
Tracks performance and anomalies using X-Ray annotations
Captures metrics like:
- Latency per record
- Data volume
- Flags (e.g., price severity)
- Shard IDs and processing times

### 🚨 Automated Alerting
- Sends SNS notifications when latency exceeds a critical threshold
- Easy to configure thresholds and topic subscriptions

### 📊 Interactive Dashboard
Built with Plotly Dash, auto-refreshes every 1 hour

Real-time visualizations of:
- Bitcoin prices
- Predicted latency (hourly & daily)
- Anomalies based on thresholds

---
## 🚀 How to run

### 🔐 AWS Credentials Setup (Required Before Running)

- This project interacts with AWS services like Kinesis, Lambda, S3, DynamoDB, and X-Ray.  
- To authorize access, you must configure AWS credentials **before running the Docker container**.

#### ✅ Step 1: Configure AWS Credentials

Run this once on your machine (if not already done):

```
aws configure
```
You’ll be prompted to enter:
- AWS Access Key ID
- AWS Secret Access Key
- Default region name (e.g., us-east-1)

#### ✅ Step 2: Pass Credentials to Docker

When running the Docker container, pass your local credentials:
```
docker run -v ~/.aws:/root/.aws -p 5000:5000 aws-xray
```
- This mounts your AWS credentials inside the container so the app can authenticate with AWS.
- Your credentials are never hardcoded or stored inside the image.

---
###  Option 1:
### 🐳 Run via Docker



#### 📦 1. Build the Docker image

```
docker build -t aws-xray .
```

#### ▶️ 2. Run the full pipeline (default mode)

```
docker run -v ~/.aws:/root/.aws -p 5000:5000 aws-xray
```

This will
- Send historical and current Bitcoin data to Kinesis
- Process and store metrics using Lambda, DynamboDB, and S3
- Analyze traces from AWS X-Ray
- Launch a dashboard at http://localhost:5000/
---

###  Option 2:
### 🧑‍💻 Run Locally (No Docker)

#### Use the provided startup script
```
./run.sh
```

#### Or manually run the python file from the project directory
```bash
python3 main.py 
```
Then Launch a dashboard at http://localhost:5000/

## 📈 Dashboard Overview
Once live, the dashboard shows:
- 📊 Predicted vs actual latency (hourly & daily)
- 🪙 Bitcoin price trends
- ⚠️ Latency anomalies
- 📉 Error rate and throughput trends (from X-Ray)
- 🔔 SNS alerts when latency exceeds threshold

---

### Open `aws_xray_example.ipynb` juypter notebook for the full end-to-end demo