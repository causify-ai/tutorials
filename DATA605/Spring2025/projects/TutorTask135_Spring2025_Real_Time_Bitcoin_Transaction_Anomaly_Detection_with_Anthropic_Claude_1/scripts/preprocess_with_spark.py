from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr, floor, when, count, avg
from datetime import datetime

# CONFIG
S3_INPUT_PATH = "s3a://btc-anomaly/raw/2025/04/21/*.json"
S3_OUTPUT_PATH = "s3a://btc-anomaly/processed/2025/04/21/output_{}.parquet".format(
    datetime.utcnow().strftime("%H%M%S")
)

def main():
    spark = SparkSession.builder \
        .appName("BTC Preprocessing with Aggregation") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "com.amazonaws.auth.DefaultAWSCredentialsProviderChain") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.endpoint", "s3.amazonaws.com") \
        .getOrCreate()

    df = spark.read.json(S3_INPUT_PATH)

    df = df.withColumn("fee_to_size_ratio", col("fee_usd") / col("size")) \
           .withColumn("input_output_ratio", col("input_count") / (col("output_count") + expr("1e-5"))) \
           .withColumn("value_diff_usd", col("input_total_usd") - col("output_total_usd")) \
           .withColumn("value_ratio", col("output_total_usd") / (col("input_total_usd") + expr("1e-5"))) \
           .withColumn("timestamp_unix", floor(col("time").cast("timestamp").cast("long"))) \
           .withColumn("time_1min", floor(col("timestamp_unix") / 60)) \
           .withColumn("time_5min", floor(col("timestamp_unix") / 300)) \
           .withColumn("is_anomalous", when((col("fee_usd") > 100) | (col("value_diff_usd").abs() > 10000), 1).otherwise(0))

    agg_1min = df.groupBy("time_1min").agg(
        count("*").alias("tx_count_1min"),
        avg("fee_usd").alias("avg_fee_1min")
    )

    df = df.join(agg_1min, on="time_1min", how="left")

    df_anomalies = df.filter("is_anomalous = 1")
    df_balanced = df.unionByName(df_anomalies).unionByName(df_anomalies)

    df_balanced.write.mode("overwrite").parquet(S3_OUTPUT_PATH)

    print(f"Preprocessed, aggregated, and balanced data saved to: {S3_OUTPUT_PATH}")

if __name__ == "__main__":
    main()