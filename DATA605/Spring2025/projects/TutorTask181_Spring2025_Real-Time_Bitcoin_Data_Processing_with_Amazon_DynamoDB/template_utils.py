"""
template_utils.py

This file contains utility functions that support the tutorial notebooks.

- Notebooks should call these functions instead of writing raw logic inline.
- This helps keep the notebooks clean, modular, and easier to debug.
- Students should implement functions here for data preprocessing,
  model setup, evaluation, or any reusable logic.
"""

import pandas as pd
import logging
from sklearn.model_selection import train_test_split
#from pycaret.classification import compare_models
from decimal import Decimal

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Example 1: Split the dataset into train and test sets
# -----------------------------------------------------------------------------

def split_data(df: pd.DataFrame, target_column: str, test_size: float = 0.2):
    """
    Split the dataset into training and testing sets.

    :param df: full dataset
    :param target_column: name of the target column
    :param test_size: proportion of test data (default = 0.2)

    :return: X_train, X_test, y_train, y_test
    """
    logger.info("Splitting data into train and test sets")
    X = df.drop(columns=[target_column])
    y = df[target_column]
    return train_test_split(X, y, test_size=test_size, random_state=42)




import requests

def get_bitcoin_price():
    """
    Fetches the current Bitcoin price in USD from the CoinGecko API.

    :return: float - latest BTC price in USD, or None if fetch fails
    """
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin",
        "vs_currencies": "usd"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        price = float(data["bitcoin"]["usd"])
        logger.info(f"Fetched Bitcoin price: ${price}")
        return price
    except Exception as e:
        logger.error(f"Error fetching Bitcoin price: {e}")
        return None


import boto3
import time

def insert_bitcoin_price(table_name="BitcoinPrices"):
    """
    Fetches current Bitcoin price and inserts it into the specified DynamoDB table.
    :param table_name: Name of your DynamoDB table
    """
    price = get_bitcoin_price()
    if price is None:
        logger.warning("Price fetch failed, skipping insert.")
        return
    price = Decimal(str(price))
    
    timestamp = int(time.time())

    try:
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.Table(table_name)

        table.put_item(
            Item={
                "timestamp": timestamp,
                "price": price
            }
        )
        logger.info(f"Inserted BTC price ${price} at timestamp {timestamp}")
    except Exception as e:
        logger.error(f"Error inserting into DynamoDB: {e}")
