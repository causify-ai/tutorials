from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("S3WriteTest").getOrCreate()

data = [("test", 1)]
df = spark.createDataFrame(data, ["name", "value"])

df.write.mode("overwrite").json("s3://bitcoin-price-streaming-data/final_windowed_output/test_write_check/")

print("✅ Write to S3 succeeded")
