import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_unixtime, col
from pyspark.sql.window import Window
from pyspark.sql.functions import avg, lag, col
from bigdl.dllib.utils.common import init_engine

init_engine()

def get_spark_session(app_name="BigDLBitcoin"):
    """
    Initialize and return a SparkSession.
    """
    return SparkSession.builder \
        .appName(app_name) \
        .getOrCreate()

def fetch_bitcoin_prices(
    api_url="https://api.coingecko.com/api/v3/coins/bitcoin/market_chart",
    vs_currency="usd",
    days=1
):
    """
    Fetch recent Bitcoin price data from CoinGecko.
    Returns a Spark DataFrame with columns:
      - timestamp (ms since epoch)
      - price     (USD as float)
    """
    resp = requests.get(api_url, params={"vs_currency": vs_currency, "days": days})
    resp.raise_for_status()
    prices = resp.json().get("prices", [])
    records = [{"timestamp": ts, "price": p} for ts, p in prices]
    spark = get_spark_session()
    return spark.createDataFrame(records)


def process_bitcoin_data(df):
    """
    Clean & prepare the raw DataFrame:
      - Convert timestamp (ms) → Spark Timestamp
      - Cast price to double
      - Select only (time, price) and order by time
    """
    df_ts = df.withColumn("time", from_unixtime(col("timestamp") / 1000).cast("timestamp"))
    df_cast = df_ts.withColumn( "price", col("price").cast("double"))
    df_sel = df_cast.select("time", "price")
    df_clean = df_sel.orderBy("time")

    return df_clean

def transform_bitcoin_data(df):
    df_long = df.withColumn("time_long", col("time").cast("long"))
    # rolling window
    w_range = Window.orderBy("time_long").rangeBetween(-3600, 0)
    # simple ordering window for lag
    w_order = Window.orderBy("time_long")

    df_avg = df_long.withColumn("rolling_avg_1h", avg("price").over(w_range))
    df_lag = df_avg.withColumn("prev_price", lag("price", 1).over(w_order))
    df_pct = df_lag.withColumn(
        "pct_change",
        (col("price") - col("prev_price")) / col("prev_price") * 100
    )
    return df_pct.drop("prev_price", "time_long")

def load_bitcoin_data(df, output_path, format="parquet", mode="overwrite"):
    """
    Persist the DataFrame to storage.
    - format: "parquet", "csv", "json", etc.
    - mode: e.g., "overwrite", "append"
    """
    df.write.format(format).mode(mode).save(output_path)


if __name__ == "__main__":
    spark = get_spark_session()
    raw_df   = fetch_bitcoin_prices(days=1)
    clean_df = process_bitcoin_data(raw_df)
    clean_df.show(10, truncate=False)
    spark.stop()
