# Real-Time Bitcoin Price Anomaly Detection Project

This project detects real-time anomalies in Bitcoin price using **Amazon Kinesis**, **Apache Flink**, **AWS Lambda**, **SNS**, **S3**, and **QuickSight**. It features a full end-to-end big data + ML pipeline for ingestion, processing, model scoring, alerting, and dashboarding.

---

## Project Structure

```
btc-anomaly-project/
│
├── AmazonKinesisExample.py           # Sends BTC price data to Kinesis stream
├── utils.py                     # Helper functions: fetch BTC price, detect anomaly
├── handler.py                   # AWS Lambda function for scoring anomalies
├── Dockerfile                   # Docker setup to run producer inside container
├── .env                         # AWS credentials and environment variables (not committed)
├── lambda.zip                   # Deployment package for Lambda (optional)
├── isolation_forest_model.pkl   # Trained anomaly detection model (used in Lambda)
├── firehose-config.json         # JSON config for Firehose S3 delivery
├── BTC_Anomaly_Complete_Project.ipynb     # Final report notebook
├── BTC_Anomaly_Technologies_Used.ipynb    # Technologies overview notebook
└── README.md                    # This file
```

---

##  Setup Instructions

### 1. Configure AWS Access
Either:
- Create `.env` file with credentials:
  ```env
  AWS_ACCESS_KEY_ID=xxx
  AWS_SECRET_ACCESS_KEY=xxx
  AWS_DEFAULT_REGION=us-east-1
  ```

---

### 2. Install Dependencies
If running locally:
```bash
pip install boto3 requests numpy
#or run
pip install requirements.txt
``` 

---

### 3. Run the BTC Data Producer
To push real-time data to Kinesis:
```bash
python send_to_kinesis.py
```

---

### 4. Train the ML Model (if needed)
Trains Isolation Forest and saves as `isolation_forest_model.pkl`:
```python
from sklearn.ensemble import IsolationForest
# see BTC_Anomaly_Complete_Project.ipynb for code
```

---

### 5. Lambda + Firehose Setup
- Package Lambda using Docker or manually
- Deploy and attach to Kinesis stream
- Firehose delivers anomaly records to S3
- SNS sends anomaly alerts

---

### 6. Visualization
- Create Athena table over S3 data
- Connect QuickSight to Athena
- Build dashboard for:
  - Price trends
  - Anomaly highlights

---

## Dependencies

- `boto3`, `requests`, `numpy`, `scikit-learn`
- AWS services: Kinesis, Lambda, Firehose, S3, SNS, Athena, QuickSight

---

## Notes
- This project simulates anomalies and flags them with an ML model.
- S3 buckets, roles, and Lambda permissions must be correctly set.
- Use CloudWatch to debug Lambda and monitor logs.