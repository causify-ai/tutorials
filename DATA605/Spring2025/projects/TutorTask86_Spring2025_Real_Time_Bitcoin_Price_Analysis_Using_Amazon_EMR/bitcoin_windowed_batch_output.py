from pyspark.sql import SparkSession
from pyspark.sql.functions import to_timestamp, window, avg
from pyspark.sql.types import StructType, StringType, DoubleType

# 1. Start Spark session
spark = SparkSession.builder.appName("BitcoinBatchWindowedAggregation").getOrCreate()
spark.sparkContext.setLogLevel("INFO")

# 2. Define schema
schema = StructType() \
    .add("timestamp", StringType()) \
    .add("price_usd", DoubleType())

# 3. Read ALL existing files from S3
df = spark.read \
    .schema(schema) \
    .json("s3://bitcoin-price-streaming-data/data_v2/")

# 4. Convert to timestamp
df = df.withColumn("timestamp", to_timestamp("timestamp"))

# 5. Perform 5-minute windowed average
agg = df.groupBy(window("timestamp", "5 minutes")).agg(avg("price_usd").alias("avg_price_usd"))

# 6. Write output to S3
agg.write \
    .mode("overwrite") \
    .json("s3://bitcoin-price-streaming-data/final_batch_output/")
