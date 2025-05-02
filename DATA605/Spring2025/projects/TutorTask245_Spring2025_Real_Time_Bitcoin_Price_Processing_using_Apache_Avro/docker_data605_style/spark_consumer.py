from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, window, avg
from pyspark.sql.types import StructType, StructField, LongType, DoubleType, StringType
import os
from pyspark.sql.functions import col, from_unixtime

# Build Spark session
spark = SparkSession.builder \
    .appName("BitcoinPriceConsumer") \
    .master("local[*]") \
    .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0") \
    .getOrCreate()


# Define the Avro schema manually as Spark StructType
schema = StructType([
    StructField("timestamp", LongType(), True),
    StructField("price", DoubleType(), True),
    StructField("currency", StringType(), True),
    StructField("volume", DoubleType(), True)
])

# Read from Kafka topic 'bitcoin_prices'
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "bitcoin_prices") \
    .option("startingOffsets", "latest") \
    .load()

# The 'value' column contains Avro binary data.
# But Spark by default reads Kafka 'value' as bytes.
# Let's decode assuming it's small JSON structure for now.

# Convert 'value' bytes to String first
kafka_df = kafka_df.selectExpr("CAST(value AS STRING) as value")

# Parse the value column as JSON
parsed_df = kafka_df.select(from_json(col("value"), schema).alias("data"))

# Flatten the structure
price_df = parsed_df.select(
    from_unixtime(col("data.timestamp")).cast("timestamp").alias("timestamp"),
    col("data.price").alias("price"),
    col("data.currency").alias("currency"),
    col("data.volume").alias("volume")
)

# Basic time-series aggregation: 5-minute moving average
moving_avg_df = price_df.withWatermark("timestamp", "10 minutes") \
    .groupBy(window(col("timestamp"), "5 minutes", "1 minute")) \
    .agg(avg("price").alias("avg_price"))

# Write results to Parquet files
query = moving_avg_df.writeStream \
    .outputMode("append") \
    .format("parquet") \
    .option("path", "/workspace/output/bitcoin_price_avg/") \
    .option("checkpointLocation", "/workspace/output/checkpoints/") \
    .start()

query.awaitTermination()
