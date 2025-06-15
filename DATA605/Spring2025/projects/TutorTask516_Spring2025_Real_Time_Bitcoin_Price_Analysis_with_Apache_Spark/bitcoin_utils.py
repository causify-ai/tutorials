import os
import requests
import pandas as pd
import time
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, window, avg
from pyspark.sql.types import StructType, StringType, DoubleType


def fetch_bitcoin_price(max_retries=5, base_delay=2, verbose=True):
    """
    Fetch the current Bitcoin price in USD from the CoinGecko API.

    Implements exponential backoff retry logic in case of API rate limits or connection errors.

    Parameters:
        max_retries (int): Maximum number of retry attempts. Default is 5.
        base_delay (int): Base delay in seconds for exponential backoff. Default is 2.
        verbose (bool): If True, prints the price and timestamp. Default is True.

    Returns:
        dict: A dictionary with:
            - 'timestamp': ISO-formatted timestamp of the request
            - 'price': Current Bitcoin price in USD (or None if request failed)
    """
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"

    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 429:
                time.sleep(base_delay * (2 ** attempt))
                continue
            response.raise_for_status()
            price = response.json()['bitcoin']['usd']
            timestamp = datetime.now().isoformat()
            if verbose:
                print(f"[{timestamp}] Price: ${price:.2f}")
            return {'timestamp': timestamp, 'price': price}
        except Exception as e:
            time.sleep(base_delay * (2 ** attempt))

    return {'timestamp': datetime.now().isoformat(), 'price': None}


def start_data_collection(output_dir="data", interval=15, num_points=1000):
    """
    Continuously fetches Bitcoin price data and writes it to CSV files.

    Parameters:
        output_dir (str): Directory where CSV files will be saved. Defaults to "data".
        interval (int): Time (in seconds) between API requests. Defaults to 15.
        num_points (int): Number of records to collect. Defaults to 1000.

    Each CSV file contains one price record with the current timestamp and price.
    The file is named using the record number and timestamp for uniqueness.
    """
    os.makedirs(output_dir, exist_ok=True)

    for i in range(num_points):
        record = fetch_bitcoin_price(verbose=False)
        if record["price"] is not None:
            filename = f"{output_dir}/record_{i}_{record['timestamp'].replace(':', '-').replace('.', '-')}.csv"
            pd.DataFrame([record]).to_csv(filename, index=False, header=False)
            print(f"[Writer] Record {i+1} saved at {record['timestamp']} → ${record['price']}")
        else:
            print(f"[Writer] Record {i+1} skipped (fetch failed).")

        time.sleep(interval)


def start_spark_stream(data_dir="data"):
    """
    Initializes a Spark Structured Streaming session and reads streaming data from CSV files.

    Parameters:
        data_dir (str): The directory where streaming CSV files are located. Defaults to "data".

    Returns:
        tuple: (spark session, streaming DataFrame)
            - spark (SparkSession): The initialized Spark session.
            - df (DataFrame): A streaming DataFrame with schema (timestamp: str, price: float).
    
    The function expects files to have no header and two columns:
        1. timestamp (ISO format)
        2. price (float in USD)
    """
    spark = SparkSession.builder.appName("BitcoinPriceStream").getOrCreate()

    schema = StructType() \
        .add("timestamp", StringType()) \
        .add("price", DoubleType())

    df = spark.readStream \
        .option("sep", ",") \
        .option("header", "false") \
        .schema(schema) \
        .csv(data_dir)

    return spark, df


def compute_moving_average(
    stream_df,
    window_size="1 minute",
    slide_interval="15 seconds",
    watermark="30 seconds",
    output_dir="moving_avg_output"
):
    """
    Compute moving average over a time window from a Spark streaming DataFrame.

    Parameters:
        stream_df (DataFrame): A Spark streaming DataFrame containing 'timestamp' and 'price' columns.
        window_size (str): Duration of the time window (e.g., "1 minute"). Default is "1 minute".
        slide_interval (str): Interval at which the window moves (e.g., "15 seconds"). Default is "15 seconds".
        watermark (str): Watermark delay to handle late data. Default is "30 seconds".
        output_dir (str): Directory to write the resulting CSV output. Default is "moving_avg_output".

    Returns:
        StreamingQuery: A Spark StreamingQuery object for the running write stream.
    
    Notes:
        - This function adds an 'event_time' column from the 'timestamp' string.
        - Aggregates price using a sliding window and computes the average.
        - Output includes 'window_start', 'window_end', and 'moving_avg' columns.
        - Data is written incrementally in append mode with a checkpoint for fault tolerance.
    """
    # Add timestamp column for event time processing
    df = stream_df.withColumn("event_time", to_timestamp(col("timestamp")))

    # Compute moving average using windowing
    ma_df = df \
        .withWatermark("event_time", watermark) \
        .groupBy(window(col("event_time"), window_size, slide_interval)) \
        .agg(avg("price").alias("moving_avg"))

    # Flatten window struct for output
    ma_df = ma_df.withColumn("window_start", col("window.start")) \
                 .withColumn("window_end", col("window.end")) \
                 .drop("window")

    # Write stream to CSV
    query = ma_df.writeStream \
        .outputMode("append") \
        .format("csv") \
        .option("path", output_dir) \
        .option("checkpointLocation", output_dir + "_checkpoint") \
        .option("header", "true") \
        .start()

    return query


def launch_writer(data_dir, interval, num_points):
    """
    Starts the data collection writer process that fetches real-time Bitcoin prices
    and writes them to CSV files in the configured data directory.
    """
    print("[Writer] Starting data collection...")
    start_data_collection(output_dir=data_dir, interval=interval, num_points=num_points)


def launch_spark_stream(delay, data_dir, window_sizes, watermark, slide_interval):
    """
    Initializes a Spark session and launches multiple streaming queries,
    one for each configured window size.

    Returns:
        List of StreamingQuery objects, one for each moving average stream.
    """
    print(f"[Spark] Waiting {delay}s to let writer populate files...")
    time.sleep(delay)

    print("[Spark] Starting Spark session...")
    spark, df = start_spark_stream(data_dir=data_dir)

    queries = []
    for win in window_sizes:
        win_safe = win.replace(" ", "_")
        output_dir = f"moving_avg_output_{win_safe}"
        print(f"[Spark] Starting stream for WINDOW_SIZE={win} → Output: {output_dir}")

        query = compute_moving_average(
            df,
            watermark=watermark,
            window_size=win,
            slide_interval=slide_interval,
            output_dir=output_dir
        )
        queries.append(query)

    print(f"[Spark] All streaming queries started ({len(queries)} total).")
    return queries, spark


