import os
import requests
import time
import shutil
import pyspark.sql
import pyspark.sql.functions as F
import pyspark.sql.window as W
 
class BitcoinDataHandler:
    def __init__(self, spark: pyspark.sql.SparkSession) -> None:
        """
        Initialize BitcoinDataHandler instance. Stop_signal corresponds to starting/stopping automatic data updates.
        Stop_signal is set to False (data will be automatically loaded by default).
        
        :param spark: SparkSession in which views will be created and queries are run.
        """
        self.spark = spark
        self.stop_signal = False

    def load_data(self, total_days: int, view_name: str, data_path: str, currency: str = "usd") -> None:
        """
        Populate the view btc_prices with past total_days information of Bitcoin prices in given currency.
        
        :param total_days: How many past days of data to load into the view.
        :param view_name: Name of the view to create and load the data into.
        :param data_path: Directory under which to store the CSV format of the data.
        :param currency: In what currency to load the data into the view; default is USD.
        """
        now_ts = int(time.time())
        from_ts = now_ts - total_days * 86400
        self.spark.catalog.dropTempView(view_name)
        if os.path.exists(data_path):
            shutil.rmtree(data_path)
        print(f"Cleared view {view_name}.")
        print(f"Fetching Bitcoin data.")
        data = self.fetch_data_range(from_ts, now_ts, currency=currency)
        if not data:
            print("No data found.")
            return
        df = self.spark.createDataFrame(data)
        if total_days > 90:
            df = df.withColumn("price_date", F.from_unixtime("timestamp", "yyyy-MM-dd"))
        else:
            df = df.withColumn("price_date", F.from_unixtime("timestamp", "yyyy-MM-dd HH:mm:ss"))
        df = df.drop_duplicates()
        df.createOrReplaceTempView(view_name)
        df.write.option("header", "true").mode("overwrite").csv(data_path)
        print(f"Created view {view_name} and updated with {df.count()} rows.")
        
    def fetch_data_range(self, from_ts: int, to_ts: int, currency: str = "usd") -> list:
        """
        Fetch and return price data using a precise time range and currency of Bitcoin.
        
        :param from_ts: Start timestamp of when to retrieve data.
        :param to_ts: End timestamp of when to retrieve data.
        :param currency: Currency in which to retrieve Bitcoin price data; default is USD.
        """
        retrieved_data = []
        url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range"
        params = {
            "vs_currency": currency,
            "from": from_ts,
            "to": to_ts
        }
        response = requests.get(url, params=params).json()
        for price in response.get("prices", []):
            retrieved_data.append({
                #Convert milliseconds to seconds.
                "timestamp": price[0] / 1000, 
                "price": price[1]
            })
        return retrieved_data

    def start_real_time_update(self, days: int, vw_nm:str, path:str, curr: str = "usd") -> None:
        """
        Fetch and load existing Bitcoin price data within specified days and start real time updates. The function will 
        identify if there is new data to add (hourly level), and updates the view with any new data periodically (at every hour).
        
        :param days: How many days to retrieve data for intially.
        :param vw_nm: Name of the view to create and load data into.
        :param curr: Currency in which to retrieve the Bitcoin price data; default is USD.
        """
        
        self.stop_signal = False
        #Intially load data with specified parameters and sleep until next retrieval.
        self.load_data(total_days=days, currency=curr, view_name=vw_nm, data_path=path)
        time.sleep(3600)
        
        while not self.stop_signal:
            #Retrieve the latest timestamp in the existing view.
            latest_ts_row = self.spark.sql(f"SELECT MAX(CAST(timestamp as double)) as latest_ts FROM {vw_nm}").collect()
            latest_ts = (latest_ts_row[0]["latest_ts"]) if latest_ts_row and latest_ts_row[0]["latest_ts"] else None
            
            #Fetch data between now and latest timestamp in the existing view.
            now_ts = int(time.time())
            new_data = self.fetch_data_range(latest_ts, now_ts, currency=curr)
            print(f"Fetching new data.")

            #Filter out old data so only new price data is considered for addition. 
            filtered_data = [item for item in new_data if int(item["timestamp"]) > int(latest_ts)]
            #If there are new entries, create a dataframe, and append latest price per hour to existing data path and view.
            if filtered_data:
                existing_df = self.spark.table(vw_nm)
                existing_df2 = existing_df.withColumn("hour_key", F.date_format(F.from_unixtime("timestamp"), "yyyy-MM-dd HH:00:00"))
                existing_hour_keys = existing_df2.select("hour_key").distinct()

                #Isolate last record for each hour.
                filtered_df = self.spark.createDataFrame(filtered_data)
                filtered_df = filtered_df.withColumn("hour_key", F.date_format(F.from_unixtime("timestamp"), "yyyy-MM-dd HH:00:00"))
                window = W.Window.partitionBy("hour_key").orderBy(F.col("timestamp").desc())
                ranked_df = filtered_df.withColumn("rn", F.row_number().over(window))
                new_df = ranked_df.filter(F.col("rn") == 1)
                
                #Exclude data for hours that are already in the view.
                new_df = new_df.join(existing_hour_keys, on="hour_key", how="left_anti")
                new_df = new_df.drop("rn","hour_key")
                new_df = new_df.withColumn("price_date", F.from_unixtime("timestamp", "yyyy-MM-dd HH:mm:ss"))
                
                #Update data path and view.
                combined_df = self.spark.read.option("header", "true").csv(path)
                new_df.write.mode("append").option("header", "false").csv(path)
                
                combined_df = existing_df.unionByName(new_df)
                self.spark.catalog.dropTempView(vw_nm)
                combined_df.createOrReplaceTempView(vw_nm)
                print(f"Added following new record(s):")
                print(new_df.show())
            else:
                print("No new data found.")
            time.sleep(3600)
    
    def stop_real_time_update(self) -> None:
        """
        Stop the real time updates. 
        """
        self.stop_signal = True
        print("Real-time hourly updates stopped.")



 