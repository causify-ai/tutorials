from dagster import job
from .ops import fetch_bitcoin_price, process_data, save_to_csv

@job
def bitcoin_price_pipeline():
    save_to_csv(process_data(fetch_bitcoin_price()))
