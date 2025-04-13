from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, window, avg
from pyspark.sql.types import StructType, StringType, DoubleType

# 1. Start Spark in Streaming Mode
spark = SparkSession.builder \
    .appName("BitcoinStructuredStreaming") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")  # Cleaner output

# 2. Define schema
schema = StructType() \
    .add("timestamp", StringType()) \
    .add("price_usd", DoubleType())

# 3. Read streaming data from folder (new files only)
# Simulate new data arrival (1 file per trigger)
df_stream = spark.readStream \
    .schema(schema) \
    .option("maxFilesPerTrigger", 1) \
    .json("data/streaming/")  # Folder to drop new JSON files into


# 4. Parse timestamp
df_stream = df_stream.withColumn("timestamp", to_timestamp("timestamp"))

# 5. Apply time-based window (e.g., 5-minute window, sliding every 1 minute)
windowed_df = df_stream.groupBy(
    window(col("timestamp"), "5 minutes", "1 minute")
).agg(
    avg("price_usd").alias("avg_price_usd")
)

# 6. Output to console
query = windowed_df.writeStream \
    .outputMode("complete") \
    .format("console") \
    .option("truncate", False) \
    .start()

query.awaitTermination()
