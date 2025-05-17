import time
import logging

from spark_setup import spark, hc
from data_ingestion import fetch_latest_price
from data_processing import add_lag_features
from model_training import train_model
from predict_stream import predict_stream

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    # 1) Ingest
    df_raw = fetch_latest_price(spark)
    df_raw.write.mode("append").parquet("data/raw_bitcoin_data.parquet")
    logging.info("✨ Ingestion complete")

    # 2) Process
    add_lag_features()

    # 3) Train
    train_model()

    # 4) Serve predictions continuously
    predict_stream()

if __name__ == "__main__":
    main()
