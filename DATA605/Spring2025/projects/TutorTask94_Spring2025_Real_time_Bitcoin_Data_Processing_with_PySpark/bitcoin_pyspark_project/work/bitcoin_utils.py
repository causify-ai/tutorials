from datetime import datetime, timezone
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import GBTRegressor
from pyspark.ml.regression import LinearRegression
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.functions import hour, dayofweek
from pyspark.sql.functions import unix_timestamp
from pyspark.sql.types import StructType, StringType, DoubleType
import json
import matplotlib.pyplot as plt
import os
import requests
import threading
import time
import shutil
import boto3





def initialize_spark_session():
    spark = SparkSession.builder \
        .appName("BitcoinPipeline") \
        .getOrCreate()

    return spark




def configure_streaming_paths_and_schedule():
    # Constants
    import os
    global STREAM_DIR
    STREAM_DIR = "Data/stream"
    global HISTORY_FILE
    HISTORY_FILE = "Data/bitcoin_combined.json"
    global DURATION
    DURATION = 300  # 5 minutes
    global INTERVAL
    INTERVAL = 30   # fetch every 30 seconds

    # Ensure necessary directories exist
    os.makedirs(STREAM_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)


def fetch_price_as_ohlc():
   url = "https://api.coingecko.com/api/v3/coins/markets"
   params = {"vs_currency": "usd", "ids": "bitcoin"}
   try:
       response = requests.get(url, params=params, timeout=10)
       data = response.json()[0]
       return {
                "Datetime": datetime.now(timezone.utc).isoformat(),
                "Open": data.get("current_price"),
                "High": data.get("high_24h"),
                "Low": data.get("low_24h"),
                "Close": data.get("current_price"),
                "Volume": str(data.get("total_volume", "0"))
            }
   except Exception as e:
        print("❌ Fetch error:", e)
        return None



def start_file_producer():
        start_time = time.time()
        while time.time() - start_time < DURATION:
            ohlc = fetch_price_as_ohlc()
            if ohlc:
                json_line = json.dumps(ohlc)

                # Write individual stream file
                filename = f"ohlc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                filepath = os.path.join(STREAM_DIR, filename)

                # Append to growing history log
                with open(HISTORY_FILE, "a") as f:
                    f.write(json_line + "\n")

                print("📁 Wrote:", filepath)
            time.sleep(INTERVAL)


def stream_and_display_batches():
    # Start Spark session
    spark = SparkSession.builder.appName("BitcoinFileStreaming").getOrCreate()

    # Schema for the JSON data
    schema = StructType() \
        .add("Datetime", StringType()) \
        .add("Open", DoubleType()) \
        .add("High", DoubleType()) \
        .add("Low", DoubleType()) \
        .add("Close", DoubleType()) \
        .add("Volume", StringType())

    # Read JSON files from stream directory
    stream_df = spark.readStream.schema(schema).json(STREAM_DIR)
    stream_df = stream_df.withColumn("Datetime", col("Datetime").cast("timestamp"))

    # Display new rows per batch only
    def process_batch(new_data, batch_id):
        count = new_data.count()
        if count > 0:
            print(f"\n📦 New batch {batch_id} — {count} new rows:")
            new_data.orderBy("Datetime").show(truncate=False)
        else:
            print(f"\n⏳ Batch {batch_id}: No new rows.")


def run_streaming_query_and_writer():
    # Start streaming query
    query = stream_df.writeStream \
        .foreachBatch(process_batch) \
        .outputMode("append") \
        .start()

    # Start producer in background
    producer_thread = threading.Thread(target=start_file_producer, daemon=True)
    producer_thread.start()

    # Wait 5 minutes and stop everything
    time.sleep(DURATION + 10)
    query.stop()
    print("✅ Streaming complete.")


def count_historical_records():
    file_path = "Data/bitcoin_combined.json"

    with open(file_path, "r") as f:
        line_count = sum(1 for line in f if line.strip())

    print(f"Total records: {line_count}")





def aggregate_hourly_daily_moving_average():
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import (
        col, avg, min, max, hour, date_format,
        window
    )
    from pyspark.sql.types import StructType, StringType, DoubleType

    # Start Spark session
    spark = SparkSession.builder.appName("BitcoinAggregation").getOrCreate()

    # Define schema
    schema = StructType() \
        .add("Datetime", StringType()) \
        .add("Open", DoubleType()) \
        .add("High", DoubleType()) \
        .add("Low", DoubleType()) \
        .add("Close", DoubleType()) \
        .add("Volume", StringType())

    # Load data
    df = spark.read.schema(schema).json("Data/bitcoin_combined.json")

    # Cast types
    df = df.withColumn("Datetime", col("Datetime").cast("timestamp")) \
           .withColumn("Volume", col("Volume").cast("double"))

    # Filter bad data
    global df_filtered
    df_filtered = df.filter(
        (col("Close").isNotNull()))


    # === ✅ Group by hour ===
    df_hourly = df_filtered \
        .withColumn("Hour", hour(col("Datetime"))) \
        .groupBy("Hour") \
        .agg(
            avg("Close").alias("Hourly_Avg_Close"),
            min("Close").alias("Hourly_Min_Close"),
            max("Close").alias("Hourly_Max_Close")
        ) \
        .orderBy("Hour")

    # === ✅ Group by day ===
    df_daily = df_filtered \
        .withColumn("Day", date_format(col("Datetime"), "yyyy-MM-dd")) \
        .groupBy("Day") \
        .agg(
            avg("Close").alias("Daily_Avg_Close"),
            min("Close").alias("Daily_Min_Close"),
            max("Close").alias("Daily_Max_Close")
        ) \
        .orderBy("Day")

    # === ✅ Moving Average with 1-hour rolling window ===
    df_moving_avg = df_filtered \
        .groupBy(
            window(col("Datetime"), "1 hour", "30 minutes")
        ) \
        .agg(avg("Close").alias("Moving_Avg_Close")) \
        .orderBy("window")

    # === ✅ Show results ===
    print("🔹 Hourly Aggregation:")
    df_hourly.show(truncate=False)

    print("🔹 Daily Aggregation:")
    df_daily.show(truncate=False)

    print("🔹 Moving Average (1-hour window, 30-min slide):")
    df_moving_avg.select(
        col("window.start").alias("Start"),
        col("window.end").alias("End"),
        "Moving_Avg_Close"
    ).show(truncate=False)


def count_filtered_rows():
    df_filtered.count()






def train_and_evaluate_gbt_regressor():
    from pyspark.ml.feature import VectorAssembler
    from pyspark.ml.regression import GBTRegressor   
    from pyspark.ml import Pipeline
    from pyspark.ml.evaluation import RegressionEvaluator
    from pyspark.sql.functions import unix_timestamp, hour, dayofweek

    # Step 1: Feature engineering
    df_gbt = df_filtered.withColumn("timestamp", unix_timestamp("Datetime"))
    df_gbt = df_gbt.withColumn("hour", hour("Datetime"))
    df_gbt = df_gbt.withColumn("dayofweek", dayofweek("Datetime"))

    # Step 2: Assemble features
    feature_cols = ["timestamp", "hour", "dayofweek"]
    assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")

    # Step 3: GBT Regressor
    gbt = GBTRegressor(featuresCol="features", labelCol="Close", maxIter=100)

    # Step 4: Pipeline
    pipeline = Pipeline(stages=[assembler, gbt])

    # Step 5: Train/test split
    train_data, test_data = df_gbt.randomSplit([0.8, 0.2], seed=42)

    # Step 6: Train model
    model = pipeline.fit(train_data)

    # Step 7: Predict
    global predictions
    predictions = model.transform(test_data)

    # Step 8: Evaluate
    evaluator = RegressionEvaluator(labelCol="Close", predictionCol="prediction", metricName="r2")
    r2 = evaluator.evaluate(predictions)

    rmse_eval = RegressionEvaluator(labelCol="Close", predictionCol="prediction", metricName="rmse")
    rmse = rmse_eval.evaluate(predictions)

    predictions.selectExpr("timestamp as timestamp_numeric", "Close", "prediction").show(10, truncate=False)

    print(f"✅ GBT R²: {r2:.4f} ({r2*100:.2f}%) variance explained")
    print(f"✅ GBT RMSE: {rmse:.2f}")

    # ✅ Save locally as Parquet
    local_path = "bitcoin_predictions.parquet"
    predictions.select("timestamp", "Close", "prediction") \
        .write.mode("overwrite") \
        .parquet(local_path)

    # 🔒 Zip the folder
    local_dir = "bitcoin_predictions.parquet"
    zip_path = "bitcoin_predictions.zip"
    shutil.make_archive("bitcoin_predictions", 'zip', local_dir)

    print("⏫ Uploading to S3...")

    # 🧠 Load S3 configuration from environment variables
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-2")
    bucket_name = os.getenv("S3_BUCKET_NAME")

    if not all([aws_access_key, aws_secret_key, bucket_name]):
        print("❌ Missing AWS credentials or bucket name in environment. Upload skipped.")
        return

    # 🔁 Upload to the specified S3 bucket
    s3 = boto3.resource(
        's3',
        aws_access_key_id=aws_access_key, # gitleaks:allow
        aws_secret_access_key=aws_secret_key, # gitleaks:allow,
        region_name=aws_region
    )

    s3.Bucket(bucket_name).upload_file(zip_path, zip_path)

    print("✅ Upload complete.")

    

def plot_actual_vs_predicted_prices():
    import matplotlib.pyplot as plt
    import pandas as pd

    print("🔍 Fetching predictions and converting datetime safely...")

    # Convert Datetime to string in Spark to avoid timezone/pandas dtype issues
    from pyspark.sql.functions import date_format

    predictions_fixed = predictions.withColumn("Datetime", date_format("Datetime", "yyyy-MM-dd HH:mm:ss"))

    # Then convert to pandas
    pdf = predictions_fixed.select("Datetime", "Close", "prediction").orderBy("Datetime").toPandas()

    # Parse to datetime safely in Pandas
    pdf["Datetime"] = pd.to_datetime(pdf["Datetime"], format="%Y-%m-%d %H:%M:%S")

    print(pdf.head())

    if pdf.empty:
        print("⚠️ Nothing to plot — DataFrame is empty.")
        return

    plt.figure(figsize=(12, 6))
    plt.plot(pdf["Datetime"], pdf["Close"], label="Actual", color="blue")
    plt.plot(pdf["Datetime"], pdf["prediction"], label="Predicted", color="red")

    plt.title("Actual vs Predicted Bitcoin Close Price (GBTRegressor)")
    plt.xlabel("Datetime")
    plt.ylabel("Close Price (USD)")
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    plt.savefig("output_plot.png")
    print("📸 Saved plot to output_plot.png")
