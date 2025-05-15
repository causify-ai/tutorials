from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, DoubleType, TimestampType
from pyspark.sql.functions import from_unixtime, col, window

# Create Spark session
spark = SparkSession.builder \
    .appName("BitcoinRealTimeStreaming") \
    .getOrCreate()

# Define schema for incoming JSON
schema = StructType() \
    .add("timestamp", DoubleType()) \
    .add("price", DoubleType())

# Read streaming data from S3
df = spark.readStream \
    .schema(schema) \
    .option("maxFilesPerTrigger", 1) \
    .json("s3://bitcoin-price-streaming-data/data_v2/")

# Convert timestamp to readable format
df = df.withColumn("timestamp", from_unixtime(col("timestamp")).cast(TimestampType()))

# Windowed average price calculation
windowed_df = df.groupBy(
    window(col("timestamp"), "1 minute", "1 minute")
).avg("price").withColumnRenamed("avg(price)", "avg_price")

# Output path
output_path = "s3://bitcoin-price-streaming-data/output_streaming/"

# Write streaming results to S3
query = windowed_df.writeStream \
    .outputMode("complete") \
    .format("json") \
    .option("path", output_path) \
    .option("checkpointLocation", "s3://bitcoin-price-streaming-data/checkpoint/") \
    .start()

query.awaitTermination()
