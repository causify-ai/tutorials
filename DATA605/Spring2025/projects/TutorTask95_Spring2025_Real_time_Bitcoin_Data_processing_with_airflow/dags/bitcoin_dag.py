from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import sys

sys.path.append('/opt/airflow')
from bitcoin_utils import save_price_to_csv, compute_moving_average, upload_to_s3

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 5, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=2)
}

with DAG(
    dag_id='bitcoin_data_pipeline',
    default_args=default_args,
    description='DAG for Bitcoin price data pipeline',
    schedule_interval='@hourly',
    catchup=False,
    tags=["bitcoin", "pipeline"]
) as dag:

    fetch_and_save = PythonOperator(
        task_id='fetch_bitcoin_price',
        python_callable=save_price_to_csv
    )

    process_data = PythonOperator(
        task_id='process_data',
        python_callable=compute_moving_average
    )

    upload_results = PythonOperator(
        task_id='upload_to_s3',
        python_callable=lambda: upload_to_s3('bitcoin-price-store', 'processed/bitcoin_processed.csv')
    )


    fetch_and_save >> process_data >> upload_results
