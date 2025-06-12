# bitcoin_emr_utils.py

import requests
import json
import boto3
from datetime import datetime
import pytz

from pyspark.sql.functions import from_json, col, window
from pyspark.sql.types import StructType, StringType, DoubleType

# -------------------------------
# Producer Utility Functions
# -------------------------------

def fetch_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["bitcoin"]["usd"]
    else:
        raise Exception(f"API request failed with status code {response.status_code}")

def get_current_timestamp():
    tz = pytz.timezone("US/Eastern")
    return datetime.now(tz).isoformat()

def save_price_to_s3(bucket, folder, filename_prefix="price", price_usd=None):
    if price_usd is None:
        price_usd = fetch_bitcoin_price()
    timestamp = get_current_timestamp()
    record = {
        "timestamp": timestamp,
        "price_usd": price_usd
    }

    filename = f"{filename_prefix}_{timestamp}.json".replace(":", "-")
    key = f"{folder}/{filename}"

    s3 = boto3.client("s3")
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(record).encode("utf-8")
    )

# -------------------------------
# Consumer (Spark Streaming) Utility Functions
# -------------------------------

def define_streaming_schema():
    return StructType() \
        .add("timestamp", StringType()) \
        .add("price_usd", DoubleType())

def read_stream_from_s3(spark, input_path, schema):
    return spark.readStream \
        .format("json") \
        .schema(schema) \
        .option("maxFilesPerTrigger", 1) \
        .load(input_path)

def aggregate_windowed_average(df):
    return df.withColumn("timestamp", col("timestamp").cast("timestamp")) \
        .withWatermark("timestamp", "1 minute") \
        .groupBy(window(col("timestamp"), "1 minute")) \
        .agg({"price_usd": "avg"}) \
        .withColumnRenamed("avg(price_usd)", "avg_price")

def write_stream_to_s3(df, output_path):
    return df.writeStream \
        .outputMode("append") \
        .format("json") \
        .option("path", output_path) \
        .option("checkpointLocation", "/tmp/checkpoint") \
        .start()
