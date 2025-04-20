from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, avg, lag
from pyspark.sql.window import Window
from pyspark.sql.types import StructType, StringType, DoubleType

# Start Spark
spark = SparkSession.builder \
    .appName("BitcoinMovingAverageAnalysis") \
    .master("local[*]") \
    .getOrCreate()

# Schema for the NDJSON file
schema = StructType() \
    .add("timestamp", StringType()) \
    .add("price_usd", DoubleType())

# Load the price data
df = spark.read.json("data/bitcoin_prices.json", schema=schema)

# Convert timestamp to proper type
df = df.withColumn("timestamp", to_timestamp("timestamp"))

# Order by time
df = df.orderBy("timestamp")

# Define the window: rolling over 3 previous rows (not minutes, because we are in static batch mode)
windowSpec = Window.orderBy("timestamp").rowsBetween(-2, 0)  # 3-row moving average

# Calculate 3-row moving average
df = df.withColumn("moving_avg_price", avg("price_usd").over(windowSpec))

# Also calculate price delta from previous record
df = df.withColumn("price_delta", col("price_usd") - lag("price_usd", 1).over(Window.orderBy("timestamp")))

# Show result
print("Bitcoin Prices with Moving Average and Price Change:")
df.select("timestamp", "price_usd", "moving_avg_price", "price_delta").show()

# Stop Spark
spark.stop()
