"""
Airflow DAG to automate real-time Bitcoin data ingestion, anomaly detection with Slack alerts,
rolling statistics computation, and S3 uploads using bitcoin_utils.py.
"""

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import sys

sys.path.append('/opt/airflow')
from bitcoin_utils import (
    save_price_to_csv,
    compute_moving_average,
    upload_to_s3
)

# DAG Configuration
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 5, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    dag_id='bitcoin_data_pipeline',
    default_args=default_args,
    description='ETL DAG: Ingest, compute stats, archive, and upload Bitcoin data with Slack alerts',
    schedule_interval='@hourly',
    catchup=False,
    tags=["bitcoin", "etl", "stats", "s3", "slack", "archival"],
) as dag:

    # Task 1: Fetch and Save Bitcoin Price (includes anomaly detection, Slack alert, archive + S3 upload)
    fetch_and_save = PythonOperator(
        task_id='fetch_and_save_bitcoin_price',
        python_callable=save_price_to_csv
    )

    # Task 2: Compute rolling statistics and update processed data + S3 upload
    process_data = PythonOperator(
        task_id='compute_moving_average',
        python_callable=compute_moving_average
    )

    # Redundant uploader task if needed independently
    upload_processed = PythonOperator(
        task_id='upload_processed_csv_to_s3',
        python_callable=lambda: upload_to_s3(
            bucket_name='bitcoin-price-store',
            key_path='processed/bitcoin_processed.csv'
        )
    )

    # DAG Flow
    fetch_and_save >> process_data >> upload_processed
