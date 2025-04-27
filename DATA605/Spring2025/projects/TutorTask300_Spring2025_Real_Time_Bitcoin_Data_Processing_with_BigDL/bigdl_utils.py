import requests
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_unixtime, col

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
    Returns the cleaned DataFrame.
    """
    return (
        df
        .withColumn("time", from_unixtime(col("timestamp")/1000).cast("timestamp"))
        .withColumn("price", col("price").cast("double"))
        .select("time", "price")
        .orderBy("time")
    )

if __name__ == "__main__":
    spark = get_spark_session()
    raw_df   = fetch_bitcoin_prices(days=1)
    clean_df = process_bitcoin_data(raw_df)
    clean_df.show(10, truncate=False)
    spark.stop()
