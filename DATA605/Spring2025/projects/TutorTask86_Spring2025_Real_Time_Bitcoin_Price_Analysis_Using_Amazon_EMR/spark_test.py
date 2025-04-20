from pyspark.sql import SparkSession

# Create SparkSession
spark = SparkSession.builder \
    .appName("TestSparkSession") \
    .master("local[*]") \
    .getOrCreate()

# Confirm Spark is working
print("Spark session created successfully!")

# Stop the session
spark.stop()