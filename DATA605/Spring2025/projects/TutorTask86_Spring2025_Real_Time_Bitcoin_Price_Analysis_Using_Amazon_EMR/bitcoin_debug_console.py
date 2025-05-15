from pyspark.sql import SparkSession
from pyspark.sql.functions import to_timestamp
from pyspark.sql.types import StructType, StringType, DoubleType

# 1. Start Spark session
spark = SparkSession.builder \
    .appName("BitcoinDebugConsole") \
    .getOrCreate()

spark.sparkContext.setLogLevel("INFO")

# 2. Define schema
schema = StructType() \
    .add("timestamp", StringType()) \
    .add("price_usd", DoubleType())

# 3. Read from S3 (simulated stream)
df_stream = spark.readStream \
    .schema(schema) \
    .option("maxFilesPerTrigger", 1) \
    .json("s3://bitcoin-price-streaming-data/data/")

# 4. Parse timestamp column
df_stream = df_stream.withColumn("timestamp", to_timestamp("timestamp"))

# 5. DEBUG: Print raw parsed data to stdout (instead of saving to S3)
query = df_stream.writeStream \
    .format("console") \
    .outputMode("append") \
    .option("truncate", False) \
    .trigger(once=True) \
    .start()

query.awaitTermination()
