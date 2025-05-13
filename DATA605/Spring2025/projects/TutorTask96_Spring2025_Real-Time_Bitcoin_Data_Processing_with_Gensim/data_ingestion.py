import requests
import pandas as pd
import numpy as np
import time
from loguru import logger

# Add a file handler specifically for the price log (to a separate file)
price_logger = logger.bind()

# Add a file handler to this logger
price_logger.add("price_log.log", level="INFO", rotation="1 day", retention="7 days", compression="zip")

# FETCHING DATA FROM COINGECKO
def fetch_price():
    try:
        params ={
            'ids': 'bitcoin',
            'vs_currencies': 'usd'
        }
        url = f'https://api.coingecko.com/api/v3/simple/price'
        response = requests.get(url,params)
        data = response.json()
        return data['bitcoin']['usd']
    except:
        logger.info("Error fetching bitcoin price")

# SAVING DATA IN CSV FILE
def save(timestamp, price):
    try:
        df = pd.read_csv("data.csv")
        tempdf = pd.DataFrame({'time': [timestamp], 'price': [price]})
        tempdf['date'] = tempdf['time'].dt.date
        tempdf['time'] = tempdf['time'].dt.time
        df = pd.concat([df,tempdf])
    except:
        tempdf = pd.DataFrame({'time': [timestamp], 'price': [price]})
        tempdf['date'] = tempdf['time'].dt.date
        tempdf['time'] = tempdf['time'].dt.time
        df = tempdf.copy()
    df.to_csv("data.csv", index=False)


def data_ingest(minutes):
    if minutes==1:
        timestamp = pd.Timestamp.now()
        price = fetch_price()

        if timestamp and price:
            price_logger.info(f"Time: {timestamp} | Price: {price}")
            save(timestamp, price)
        else:
            price_logger.info("No record found")
    elif minutes>1:
        for _ in range(minutes):
        # for _ in range(60):  # Collect for x minutes
        # while True:  # Collect indefinitely
            timestamp = pd.Timestamp.now()
            price = fetch_price()

            if timestamp and price:
                logger.info(f"Time: {timestamp} | Price: {price}")
                save(timestamp, price)
            else:
                logger.info("No record found")
                
            time.sleep(60)  # Scraping data after every 60 seconds
        logger.info("Data Ingestion Module Completed")
    else:
        logger.info("Entered Data Ingestion Module")
        while True:  # Collect indefinitely
            timestamp = pd.Timestamp.now()
            price = fetch_price()

            if timestamp and price:
                logger.info(f"Time: {timestamp} | Price: {price}")
                save(timestamp, price)
            else:
                logger.info("No record found")
                
            time.sleep(60)  # Scraping data after every 60 seconds
        # logger.info("Data Ingestion Module Completed")

