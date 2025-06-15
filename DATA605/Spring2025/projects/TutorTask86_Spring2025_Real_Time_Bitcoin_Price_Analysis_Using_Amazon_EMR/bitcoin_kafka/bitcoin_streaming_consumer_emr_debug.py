from pyspark.sql import SparkSession
from pyspark.sql.functions import window, col
from pyspark.sql.types import StructType, StringType, TimestampType, IntegerType
from pyspark.sql.functions import from_json

# Initialize Spark
spark = SparkSession.builder.appName("BitcoinRealTimeStreaming").getOrCreate()

# Define schema matching your JSON input
schema = StructType() \
    .add("timestamp", StringType()) \
    .add("price_usd", IntegerType())

# Read stream from S3 (update to your correct path if different)
input_path = "s3://bitcoin-price-streaming-data/data_v2/"

# Read the streaming data
df = spark.readStream.schema(schema).json(input_path)

# Convert string timestamp to timestamp type
df = df.withColumn("timestamp", col("timestamp").cast(TimestampType()))

# Group into 1-minute windows and compute average
windowed_df = df.withWatermark("timestamp", "1 minute").groupBy(
    window("timestamp", "1 minute")
).avg("price_usd").withColumnRenamed("avg(price_usd)", "avg_price")

# Write output to S3
output_path = "s3://bitcoin-price-streaming-data/output/"
query = windowed_df.writeStream \
    .outputMode("append") \
    .format("json") \
    .option("path", output_path) \
    .option("checkpointLocation", "s3://bitcoin-price-streaming-data/checkpoints/") \
    .start()

query.awaitTermination()
