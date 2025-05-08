import os
import re
import boto3
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, window

S3_BUCKET = "btc-anomaly"
RAW_PREFIX = "raw"
PROCESSED_PREFIX = "processed"

def get_latest_date_folder(bucket, prefix):
    s3 = boto3.client("s3")
    paginator = s3.get_paginator("list_objects_v2")
    result = paginator.paginate(Bucket=bucket, Prefix=f"{prefix}/")

    folders = set()
    date_pattern = re.compile(r"raw/(\d{4})/(\d{2})/(\d{2})/")

    for page in result:
        for obj in page.get("Contents", []):
            key = obj["Key"]
            match = date_pattern.match("/".join(key.split("/")[:4]) + "/")
            if match:
                year, month, day = match.groups()
                folders.add(f"{year}/{month}/{day}")

    return sorted(folders)[-1] if folders else None

def read_json_auto_format(spark, input_path):
    try:
        return spark.read.option("mode", "FAILFAST").json(input_path)
    except:
        try:
            return spark.read.option("multiLine", "true").json(input_path)
        except Exception as e:
            raise RuntimeError(f"Failed to read JSON: {e}")

def main():
    spark = SparkSession.builder.appName("BTC Preprocessing").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    latest_folder = get_latest_date_folder(S3_BUCKET, RAW_PREFIX)
    if latest_folder is None:
        print("No raw data folder found.")
        return

    input_path = f"s3a://{S3_BUCKET}/{RAW_PREFIX}/{latest_folder}/*.json"
    df = read_json_auto_format(spark, input_path)

    time_col = next((c for c in ["time", "timestamp", "block_time"] if c in df.columns), None)
    if not time_col:
        print("No timestamp column found.")
        return

    df = df.withColumn("timestamp", to_timestamp(col(time_col)))
    df = df.filter(col("timestamp").isNotNull())
    if df.count() == 0:
        print("No rows with valid timestamps.")
        return

    agg_1min = df.groupBy(window(col("timestamp"), "1 minute")) \
                 .count().withColumnRenamed("count", "tx_count_1min")

    agg_5min = df.groupBy(window(col("timestamp"), "5 minutes")) \
                 .count().withColumnRenamed("count", "tx_count_5min")

    output_prefix = f"s3a://{S3_BUCKET}/{PROCESSED_PREFIX}/{latest_folder}"
    agg_1min.write.mode("overwrite").parquet(f"{output_prefix}/tx_agg_1min.parquet")
    agg_5min.write.mode("overwrite").parquet(f"{output_prefix}/tx_agg_5min.parquet")

if __name__ == "__main__":
    main()