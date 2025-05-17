# Real-Time Bitcoin Data Processing with Amazon DynamoDB

## Author: Varad Tambe
## Course: DATA605 Spring 2025

## Overview
This project demonstrates how to ingest real-time Bitcoin price data from the CoinGecko API and store it in Amazon DynamoDB. We then perform time-series analysis to identify trends and visualize the data using Python.

## Key Technologies:
- **CoinGecko API** — For real-time Bitcoin price data.
- **Amazon DynamoDB** — A NoSQL database for durable, scalable storage.
- **Boto3** — AWS SDK for Python to interact with DynamoDB.
- **Pandas & Matplotlib** — For analysis and visualization of price trends.
- **Jupyter Notebook** — For interactive data exploration.

---

## Project Structure:
├── dynamodb.API.md # API documentation for interacting with DynamoDB
├── dynamodb.example.md # Step-by-step example to run the project
├── README.md # Project overview and setup instructions
├── cleanup.sh # Shell script to clean up temp files and logs
├── dynamodb.API.ipynb # ipynb file for API execution
├── dynamodb.example.ipynb # ipynb file to run the actual project
├── realtime_ingestor.py # Script to fetch and store Bitcoin price data
└── template_utils.py # Utility functions for API and database interactions

## Setup Instructions:
### **Clone the Repository**
```bash
git clone <repository-link>
cd Real-Time_Bitcoin_Data_Processing_with_Amazon_DynamoDB

### **Install Dependencies**
pip install boto3 pandas matplotlib requests

### **Configure AWS Credentials**
aws configure
You should have permissions for:
AmazonDynamoDBFullAccess
AWSLambdaFullAccess

### **Create DynamoDB Table**
Run the following script to create the DynamoDB table:
python3 template_utils.py

### **Run Real-Time Data Ingestion**
To begin collecting Bitcoin prices in real-time:
python3 realtime_ingestor.py

### **Analyze Data**
Launch the Jupyter Notebook for analysis
