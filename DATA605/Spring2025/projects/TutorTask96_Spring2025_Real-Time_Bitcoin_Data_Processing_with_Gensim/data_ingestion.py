import requests
import pandas as pd
import numpy as np
import time
from loguru import logger

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
    if minutes:
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
        logger.info("Data Ingestion Module Completed")