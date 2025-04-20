from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, window, avg
from pyspark.sql.types import StructType, StringType, DoubleType

# 1. Start Spark in Streaming Mode
spark = SparkSession.builder \
    .appName("BitcoinStructuredStreaming") \
    .getOrCreate()

# ✅ Set log level to INFO for detailed logging (needed for debugging EMR failures)
spark.sparkContext.setLogLevel("INFO")

# 2. Define schema
schema = StructType() \
    .add("timestamp", StringType()) \
    .add("price_usd", DoubleType())

# 3. Read streaming data from folder (new files only)
#    Simulate new data arrival (1 file per trigger)
df_stream = spark.readStream \
    .schema(schema) \
    .option("maxFilesPerTrigger", 1) \
    .json("s3://bitcoin-price-streaming-data/data/")

# 4. Parse timestamp
df_stream = df_stream.withColumn("timestamp", to_timestamp("timestamp"))

# 5. Aggregate: average price in 5-minute windows
agg = df_stream \
    .withWatermark("timestamp", "10 minutes") \
    .groupBy(
        window("timestamp", "5 minutes")
    ) \
    .agg(avg("price_usd").alias("avg_price_usd"))

# 6. Write the results to console (can change to S3 sink later)
query = agg.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .start()

query.awaitTermination()
