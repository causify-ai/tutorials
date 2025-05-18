from pyspark.sql import SparkSession
from pyspark.sql.functions import lag, col
from pyspark.sql.window import Window

def add_lag_features(input_parquet="data/stream_data.csv",
                     output_parquet="data/processed_bitcoin_data.parquet"):
    # 1) Read your raw stream CSV into Spark
    df = (
        SparkSession.builder
        .appName("BitcoinDataProcessing")
        .master("local[*]")
        .getOrCreate()
        .read
        .option("header", "true")
        .csv(input_parquet)
    )

    # 2) Cast to correct types
    df = df.withColumn("timestamp", col("timestamp").cast("long")) \
           .withColumn("price", col("price").cast("double"))

    # 3) Add lag-1 and lag-2 features
    window = Window.orderBy("timestamp")
    df = df.withColumn("lag_1", lag("price", 1).over(window)) \
           .withColumn("lag_2", lag("price", 2).over(window)) \
           .na.drop()

    # 4) Write out for training
    df.write.mode("overwrite").parquet(output_parquet)
    print(f"✅ Processed data written to {output_parquet}")

if __name__ == "__main__":
    add_lag_features()