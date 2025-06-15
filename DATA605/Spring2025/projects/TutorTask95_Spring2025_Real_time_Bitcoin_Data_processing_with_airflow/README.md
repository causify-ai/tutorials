# Real-Time Bitcoin Data Processing with Apache Airflow

This project implements a real-time Bitcoin price data pipeline using **Apache Airflow**, **CoinGecko API**, and **AWS S3**. The pipeline includes anomaly detection, Slack alerts, snapshot archival, and rolling statistics — all orchestrated via Airflow DAGs and Dockerized for reproducibility.



##  Project Overview

-  Fetches **real-time Bitcoin price data hourly** from CoinGecko API
-  Computes **rolling mean and standard deviation**
-  Stores **raw and processed data locally and in AWS S3**
-  Sends **Slack alerts** for large 1h or 24h price changes
-  Archives timestamped raw data snapshots for historical tracking
-  Fully Dockerized Airflow setup with PostgreSQL



##  File Structure

```plaintext
.
├── dags/
│   └── bitcoin_dag.py            # Airflow DAG: defines fetch, process, upload
├── bitcoin_utils.py              # All utility logic for fetch, alerts, archive, S3
├── airflow.API.ipynb             # Demonstrates the API interaction logic
├── airflow.API.md                # Markdown explanation of how the API works
├── airflow.example.ipynb         # Notebook running full pipeline sequence
├── airflow.example.md            # Explains pipeline implementation and design
├── data/                         # Volume mount for raw/processed/snapshot CSVs
├── Dockerfile                    # Optional custom build 
├── requirements.txt              # Python dependencies
├── docker-compose.yaml           # Brings up Airflow, Postgres, volumes
````



##  Setup & Execution

### 1. Start Airflow Docker Environment

```bash
docker-compose up --build
```

Wait for containers to initialize, especially `airflow-init` and `airflow-webserver`.



### 2. Access Airflow UI

* Go to: [http://localhost:8080](http://localhost:8080)
* Login with:

  ```
  Username: admin
  Password: admin
  ```
* Trigger the DAG: `bitcoin_data_pipeline`



##  Pipeline Workflow

The DAG `bitcoin_data_pipeline` includes the following tasks:

| Step | Task ID                        | Description                                                                                             |
| ---- | ------------------------------ | ------------------------------------------------------------------------------------------------------- |
| 1️  | `fetch_and_save_bitcoin_price` | Fetch price from CoinGecko, detect anomalies, send Slack alerts, archive raw snapshot, upload raw to S3 |
| 2️  | `compute_moving_average`       | Compute moving average & std dev, save processed file, upload to S3                                     |
| 3️  | `upload_processed_csv_to_s3`   | Optional redundant upload of processed file (manually callable)                                         |


##  Configuration

### Environment Variables

These are automatically used in your Docker container:

```bash
BITCOIN_RAW_PATH=/opt/airflow/data/bitcoin_raw.csv
BITCOIN_PROCESSED_PATH=/opt/airflow/data/bitcoin_processed.csv
BITCOIN_ARCHIVE_PATH=/opt/airflow/data/archive
```

To use Slack alerts:

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
```

###  Environment Variables with `.env` File

To avoid exposing secrets (like Slack webhooks or AWS credentials) in your code or version control, you can define them in a `.env` file:

#### Sample `.env` file:

```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/your/token/here
```

Make sure to place this file **in your project root directory**, and update your `docker-compose.yaml` to include:

```yaml
env_file:
  - .env
```

For example, inside `airflow-webserver`, `airflow-scheduler`, and `airflow-init` services:

```yaml
services:
  airflow-webserver:
    ...
    env_file:
      - .env
```


##  AWS S3 Access

* Ensure your AWS credentials are located in:

  ```
  ~/.aws/credentials
  ```
* These credentials are mounted automatically via:

  ```yaml
  - ${USERPROFILE}/.aws:/home/airflow/.aws
  ```



##  Documentation

| File                                               | Description                                                                 |
|----------------------------------------------------|-----------------------------------------------------------------------------|
| [`bitcoin_utils.py`](./bitcoin_utils.py)           | Modular utility functions: fetch, alert, archive, upload                   |
| [`bitcoin_dag.py`](./dags/bitcoin_dag.py)          | Apache Airflow DAG that orchestrates the full ETL pipeline                 |
| [`airflow.API.ipynb`](./airflow.API.ipynb)         | Tool demonstration notebook — showcases how utility functions behave       |
| [`airflow.API.md`](./airflow.API.md)               | Explains each utility function's internal logic and expected behavior      |
| [`airflow.example.ipynb`](./airflow.example.ipynb) | Full project demo notebook — simulates the entire DAG workflow manually    |
| [`airflow.example.md`](./airflow.example.md)       | Describes the step-by-step pipeline execution and design rationale         |


##  Features Implemented

*  CoinGecko API integration
*  Slack alert integration
*  CSV-based data logging
*  AWS S3 backup and sync
*  Snapshot archiving
*  Modular utility design


##  References

* [CoinGecko API Docs](https://www.coingecko.com/en/api)
* [Apache Airflow TaskFlow](https://airflow.apache.org/docs/apache-airflow/stable/tutorial/taskflow.html)
* [AWS S3 Python SDK](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
* [Slack Webhooks](https://api.slack.com/messaging/webhooks)



