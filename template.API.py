# template.API.py

import requests
import pandas as pd

# Supported Blockchain.com endpoints
BLOCKCHAIN_API_URLS = {
    "hash_rate": "https://api.blockchain.info/charts/hash-rate?timespan=1days&format=json",
    "transaction_count": "https://api.blockchain.info/charts/n-transactions?timespan=1days&format=json",
    "block_size": "https://api.blockchain.info/charts/avg-block-size?timespan=1days&format=json"
}

def fetch_bitcoin_metric(metric_name):
    """
    Fetch time series data for a given Bitcoin metric.
    
    Args:
        metric_name (str): One of 'hash_rate', 'transaction_count', or 'block_size'
    
    Returns:
        pd.DataFrame: DataFrame with datetime index and a 'value' column
    """
    if metric_name not in BLOCKCHAIN_API_URLS:
        raise ValueError(f"Invalid metric: {metric_name}. Options: {list(BLOCKCHAIN_API_URLS.keys())}")

    response = requests.get(BLOCKCHAIN_API_URLS[metric_name])
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data['values'])
    df['x'] = pd.to_datetime(df['x'], unit='s')
    df.set_index('x', inplace=True)
    df.rename(columns={'y': 'value'}, inplace=True)

    return df

# Optional test
if __name__ == "__main__":
    df = fetch_bitcoin_metric("transaction_count")
    print(df.head())