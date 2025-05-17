import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, window, avg, count
from pyspark.sql.types import DoubleType, IntegerType

# Paths (resolved relative to script location)
BASE_DIR = os.path.dirname(__file__)
RAW_INPUT_DIR = os.path.join(BASE_DIR, "../data/raw/")
PROCESSED_DIR = os.path.join(BASE_DIR, "../data/processed/")

def main():
    print("[INFO] Starting Spark preprocessing...")

    spark = SparkSession.builder \
        .appName("BitcoinTransactionPreprocessing") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    df = spark.read.option("multiLine", True).json(f"{RAW_INPUT_DIR}/*.json")

    if "timestamp" not in df.columns:
        print("[ERROR] Timestamp column not found in input data.")
        return

    # Cast and clean
    df = df.withColumn("timestamp", to_timestamp(col("timestamp"))).dropna(subset=["timestamp"])
    df = df.withColumn("value", col("value").cast(DoubleType()))
    df = df.withColumn("fee", col("fee").cast(DoubleType()))
    df = df.withColumn("fee_to_value_ratio", col("fee_to_value_ratio").cast(DoubleType()))
    df = df.withColumn("input_count", col("input_count").cast(IntegerType()))
    df = df.withColumn("output_count", col("output_count").cast(IntegerType()))

    df_cleaned = df.select(
        "timestamp", "tx_hash", "block_id", "value", "fee", "fee_to_value_ratio",
        "input_count", "output_count", "size"
    )

    # Aggregated feature averages (1-min)
    agg_1min = df_cleaned.groupBy(window("timestamp", "1 minute")).agg(
        avg("value").alias("avg_value"),
        avg("fee").alias("avg_fee"),
        avg("fee_to_value_ratio").alias("avg_fee_to_value_ratio"),
        avg("input_count").alias("avg_input_count"),
        avg("output_count").alias("avg_output_count"),
        avg("size").alias("avg_tx_size")
    ).withColumn("window_start", col("window.start")) \
     .withColumn("window_end", col("window.end")) \
     .drop("window")

    # Aggregated feature averages (5-min)
    agg_5min = df_cleaned.groupBy(window("timestamp", "5 minutes")).agg(
        avg("value").alias("avg_value"),
        avg("fee").alias("avg_fee"),
        avg("fee_to_value_ratio").alias("avg_fee_to_value_ratio"),
        avg("input_count").alias("avg_input_count"),
        avg("output_count").alias("avg_output_count"),
        avg("size").alias("avg_tx_size")
    ).withColumn("window_start", col("window.start")) \
     .withColumn("window_end", col("window.end")) \
     .drop("window")

    # NEW: Transaction count per 1-minute window (for EWMA)
    count_1min = df_cleaned.groupBy(window("timestamp", "1 minute")).agg(
        count("*").alias("tx_count_1min")
    ).withColumn("window_start", col("window.start")) \
     .drop("window")

    # Save all
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    df_cleaned.toPandas().to_csv(os.path.join(PROCESSED_DIR, "cleaned_transactions.csv"), index=False)
    agg_1min.toPandas().to_csv(os.path.join(PROCESSED_DIR, "tx_agg_1min.csv"), index=False)
    agg_5min.toPandas().to_csv(os.path.join(PROCESSED_DIR, "tx_agg_5min.csv"), index=False)
    count_1min.toPandas().to_csv(os.path.join(PROCESSED_DIR, "tx_count_1min.csv"), index=False)

    print("[INFO] Spark preprocessing completed. Files saved to data/processed/")

if __name__ == "__main__":
    main()