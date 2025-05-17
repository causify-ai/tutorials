from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, from_unixtime, window, avg, stddev, count, lag, when
from pyspark.sql.types import StructType, StructField, LongType, DoubleType, StringType
from pyspark.sql.window import Window

# --------------------------------------------------------------------------------
# 1. Initialize Spark session
# --------------------------------------------------------------------------------
spark = SparkSession.builder \
    .appName("BitcoinPriceConsumer") \
    .master("local[*]") \
    .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0") \
    .getOrCreate()

# --------------------------------------------------------------------------------
# 2. Define Avro schema as StructType
# --------------------------------------------------------------------------------
schema = StructType([
    StructField("timestamp", LongType(), True),
    StructField("price", DoubleType(), True),
    StructField("currency", StringType(), True),
    StructField("volume", DoubleType(), True)
])

# --------------------------------------------------------------------------------
# 3. Read stream from Kafka topic
# --------------------------------------------------------------------------------
kafka_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092")  \
    .option("subscribe", "bitcoin_prices") \
    .option("startingOffsets", "latest") \
    .load()

# Decode value from bytes to JSON string, then parse it
kafka_df = kafka_df.selectExpr("CAST(value AS STRING) as value")
parsed_df = kafka_df.select(from_json(col("value"), schema).alias("data"))

# Flatten parsed data
price_df = parsed_df.select(
    from_unixtime(col("data.timestamp")).cast("timestamp").alias("timestamp"),
    col("data.price").alias("price"),
    col("data.currency").alias("currency"),
    col("data.volume").alias("volume")
)

# --------------------------------------------------------------------------------
# 4. Compute 5-minute moving average of price
# --------------------------------------------------------------------------------
moving_avg_df = price_df.withWatermark("timestamp", "10 minutes") \
    .groupBy(window(col("timestamp"), "5 minutes", "1 minute")) \
    .agg(avg("price").alias("avg_price"))

# --------------------------------------------------------------------------------
# 5. Label price trends (rising, falling, stable)
# --------------------------------------------------------------------------------
trend_df = moving_avg_df.select(
    col("window.start").alias("start"),
    col("window.end").alias("end"),
    col("avg_price")
)

trend_window = Window.orderBy("start")

trend_df = trend_df.withColumn("prev_price", lag("avg_price").over(trend_window)) \
    .withColumn(
        "trend",
        when(col("avg_price") > col("prev_price") * 1.01, "rising")
        .when(col("avg_price") < col("prev_price") * 0.99, "falling")
        .otherwise("stable")
    )

# --------------------------------------------------------------------------------
# 6. Compute volatility (standard deviation of price)
# --------------------------------------------------------------------------------
volatility_df = price_df.withWatermark("timestamp", "10 minutes") \
    .groupBy(window(col("timestamp"), "5 minutes", "1 minute")) \
    .agg(
        avg("price").alias("avg_price"),
        stddev("price").alias("std_dev"),
        count("price").alias("sample_count")
    )

# --------------------------------------------------------------------------------
# 7. Start write streams for each output
# --------------------------------------------------------------------------------

# Save moving averages
moving_avg_query = moving_avg_df.writeStream \
    .outputMode("append") \
    .format("parquet") \
    .option("path", "/workspace/output/bitcoin_price_avg/") \
    .option("checkpointLocation", "/workspace/output/checkpoints_avg/") \
    .start()

# Save volatility stats
volatility_query = volatility_df.writeStream \
    .outputMode("append") \
    .format("parquet") \
    .option("path", "/workspace/output/bitcoin_volatility/") \
    .option("checkpointLocation", "/workspace/output/checkpoints_volatility/") \
    .start()

# --------------------------------------------------------------------------------
# 8. Await termination of all queries
# --------------------------------------------------------------------------------
spark.streams.awaitAnyTermination()
