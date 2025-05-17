"""
template_utils.py

Utility functions for real-time Bitcoin analysis with PySparkling.

- Fetch live Bitcoin prices via CoinGecko.
- Wrap results in pandas DataFrames.
- Convert pandas DataFrame → Spark DataFrame with explicit schema.
- Run H2O AutoML on a Spark DataFrame.
"""

import logging
from datetime import datetime

import requests
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, TimestampType, DoubleType
from pysparkling import H2OContext
from h2o.automl import H2OAutoML

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Data Fetching
# -----------------------------------------------------------------------------
def fetch_bitcoin_price() -> float:
    """
    Fetch the current Bitcoin price in USD from CoinGecko.
    :return: price as Python float
    """
    url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    price = float(data['bitcoin']['usd'])
    logger.debug("Fetched Bitcoin price: %s", price)
    return price

def fetch_data() -> pd.DataFrame:
    """
    Wrap the latest price into a one-row pandas DataFrame
    with UTC timestamp and float price.
    """
    price = fetch_bitcoin_price()
    ts = datetime.utcnow()
    df = pd.DataFrame([{"timestamp": ts, "price": price}])
    logger.debug("Wrapped data into DataFrame:\n%s", df)
    return df

# -----------------------------------------------------------------------------
# Spark Conversion
# -----------------------------------------------------------------------------
def to_spark_df(spark: SparkSession, pdf: pd.DataFrame):
    """
    Convert a pandas DataFrame (datetime + float) into a Spark DataFrame
    using an explicit schema so types align for TimestampType and DoubleType.
    """
    # Ensure python datetimes and float types
    pdf = pdf.copy()
    pdf['timestamp'] = pdf['timestamp'].dt.to_pydatetime()
    pdf['price'] = pdf['price'].astype(float)

    schema = StructType([
        StructField("timestamp", TimestampType(), nullable=True),
        StructField("price",     DoubleType(),    nullable=True),
    ])
    sdf = spark.createDataFrame(pdf, schema=schema)
    logger.debug("Converted to Spark DataFrame with schema %s", sdf.schema)
    return sdf

# -----------------------------------------------------------------------------
# AutoML
# -----------------------------------------------------------------------------
def run_automl(hc: H2OContext, sdf, target_col: str = "price",
               max_models: int = 5, max_runtime_secs: int = 30, seed: int = 42):
    """
    Upload Spark DataFrame to H2O, run AutoML, and return the AutoML object.
    """
    # Convert to H2OFrame
    hf = hc.as_h2o_frame(sdf, framename="bitcoin_data")
    logger.info("Starting H2O AutoML with max_models=%s, max_runtime_secs=%s",
                max_models, max_runtime_secs)
    aml = H2OAutoML(max_models=max_models,
                    max_runtime_secs=max_runtime_secs,
                    seed=seed)
    aml.train(y=target_col, training_frame=hf)
    logger.info("AutoML run complete. Leader model: %s", aml.leader.model_id)
    return aml
