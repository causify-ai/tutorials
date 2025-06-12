from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StringType, DoubleType
from pyspark.sql.functions import to_timestamp

spark = SparkSession.builder.appName("BitcoinReadTest").getOrCreate()
spark.sparkContext.setLogLevel("INFO")

print("✅ Spark session started")

schema = StructType() \
    .add("timestamp", StringType()) \
    .add("price_usd", DoubleType())

print("📥 Reading from S3...")

df = spark.read.schema(schema).json("s3://bitcoin-price-streaming-data/data_v2/")

print("🕒 Parsing timestamp...")

df = df.withColumn("timestamp", to_timestamp("timestamp"))

print("📊 Showing data...")

df.show(truncate=False)

print("✅ Done.")
