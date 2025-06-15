from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window
from pyspark.sql.types import StructType, DoubleType, TimestampType

# 1. Start Spark Session
spark = SparkSession.builder \
    .appName("BitcoinRealTimeStreaming") \
    .master("local[*]") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# 2. Define Schema of incoming Kafka JSON
schema = StructType() \
    .add("timestamp", DoubleType()) \
    .add("price", DoubleType())

# 3. Read from Kafka Topic
raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "bitcoin_price") \
    .load()

# 4. Parse and Convert JSON
parsed_df = raw_df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*") \
    .withColumn("timestamp", col("timestamp").cast(TimestampType()))

# 5. Aggregate over 1-minute window
agg_df = parsed_df \
    .withWatermark("timestamp", "1 minute") \
    .groupBy(window(col("timestamp"), "1 minute")) \
    .avg("price") \
    .withColumnRenamed("avg(price)", "avg_price")

# 6. Write output to console
query = agg_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .start()

query.awaitTermination()
