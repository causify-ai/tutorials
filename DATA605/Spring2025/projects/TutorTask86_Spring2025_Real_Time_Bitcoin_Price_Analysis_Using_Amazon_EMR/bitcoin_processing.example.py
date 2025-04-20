from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_timestamp, avg, min, max
from pyspark.sql.types import StructType, StringType, DoubleType

# Start Spark
spark = SparkSession.builder \
    .appName("BitcoinPriceProcessing") \
    .master("local[*]") \
    .getOrCreate()

# Define the schema
schema = StructType() \
    .add("timestamp", StringType()) \
    .add("price_usd", DoubleType())

# Load the JSON file (NDJSON format)
df = spark.read.json("data/bitcoin_prices.json", schema=schema)

# Convert timestamp string to actual timestamp type
df = df.withColumn("timestamp", to_timestamp("timestamp"))

# Show the raw data
print("Raw Bitcoin Data:")
df.show()

# Basic stats
print("Summary Stats:")
df.select(
    avg("price_usd").alias("avg_price"),
    min("price_usd").alias("min_price"),
    max("price_usd").alias("max_price")
).show()

# Stop Spark
spark.stop()
