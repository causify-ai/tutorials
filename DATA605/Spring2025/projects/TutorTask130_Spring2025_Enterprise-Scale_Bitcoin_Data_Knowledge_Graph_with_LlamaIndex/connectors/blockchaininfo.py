import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BlockchainInfoConnector:
    """
    Connector for the Blockchain.info API to fetch on-chain metrics for Bitcoin.
    """
    
    BASE_URL = "https://api.blockchain.info/charts"
    
    # Mapping of our metric names to Blockchain.info chart names
    METRIC_MAPPING = {
        "transaction_volume_btc": "n-transactions",  # Transaction count
        "transaction_volume_usd": "estimated-transaction-volume-usd",  # Transaction volume in USD
        "active_addresses": "n-unique-addresses",  # Number of active addresses
        #"mvrv": "mvrv",  # Market Value to Realized Value
        "transaction_fees": "transaction-fees",  # Total transaction fees in BTC
        "mempool_size": "mempool-size",  # Size of the mempool in bytes
        "hash_rate": "hash-rate",  # Network hash rate
        "difficulty": "difficulty",  # Network difficulty
        "utxo_set_size": "utxo-count"  # UTXO set size
    }
    
    def __init__(self, rate_limit_delay: float = 2.0):
        """
        Initialize the BlockchainInfoConnector.
        """
        self.rate_limit_delay = rate_limit_delay # in seconds
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a request to the Blockchain.info API.
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            logger.info(f"Requesting data from {url} with params {params}")
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            # Add a delay to respect rate limits
            time.sleep(self.rate_limit_delay)
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to {url}: {e}")
            raise
    
    def _format_timestamp(self, ts: Optional[Union[int, datetime]]) -> Optional[int]:
        """
        Format a timestamp to Unix timestamp in seconds.
        """
        if ts is None:
            return None
        
        if isinstance(ts, datetime):
            return int(ts.timestamp())
        
        return int(ts)
    
    def get_metric(
        self, 
        metric_name: str, 
        start_ts: Optional[Union[int, datetime]] = None,
        end_ts: Optional[Union[int, datetime]] = None,
        timespan: str = "all",
    ) -> Dict[str, Any]:
        """
        Get a metric from the Blockchain.info API.
        """
        if metric_name not in self.METRIC_MAPPING:
            raise ValueError(f"Unknown metric: {metric_name}. Available metrics: {list(self.METRIC_MAPPING.keys())}")
        
        chart_name = self.METRIC_MAPPING[metric_name]
        
        params = {
            "format": "json",
            "timespan": timespan
        }
        
        # Add start timestamp if provided
        start_ts_formatted = self._format_timestamp(start_ts)
        if start_ts_formatted is not None:
            params["start"] = start_ts_formatted
            
        # If end_ts is provided, we need to calculate a timespan
        # Blockchain.info API doesn't directly support end timestamps
        if end_ts is not None:
            end_ts_formatted = self._format_timestamp(end_ts)
            if start_ts_formatted is not None:
                # Calculate timespan based on difference between start and end
                diff_seconds = end_ts_formatted - start_ts_formatted
                # Convert to appropriate timespan format
                if diff_seconds < 86400:  # Less than a day
                    params["timespan"] = f"{diff_seconds // 3600}hours"
                elif diff_seconds < 604800:  # Less than a week
                    params["timespan"] = f"{diff_seconds // 86400}days"
                elif diff_seconds < 2592000:  # Less than a month
                    params["timespan"] = f"{diff_seconds // 604800}weeks"
                else:  # More than a month
                    params["timespan"] = f"{diff_seconds // 2592000}months"
        
        response = self._make_request(chart_name, params)
        
        # Filter response by end timestamp if needed
        if end_ts is not None:
            end_ts_formatted = self._format_timestamp(end_ts)
            response["values"] = [v for v in response["values"] if v["x"] <= end_ts_formatted]
        
        return response
    
    def get_transaction_volume_btc(self, start_ts=None, end_ts=None) -> Dict[str, Any]:
        """Get the number of Bitcoin transactions."""
        return self.get_metric("transaction_volume_btc", start_ts, end_ts)
    
    def get_transaction_volume_usd(self, start_ts=None, end_ts=None) -> Dict[str, Any]:
        """Get the estimated transaction volume in USD."""
        return self.get_metric("transaction_volume_usd", start_ts, end_ts)
    
    def get_active_addresses(self, start_ts=None, end_ts=None) -> Dict[str, Any]:
        """Get the number of unique active addresses."""
        return self.get_metric("active_addresses", start_ts, end_ts)
    
    # todo: couldn't find mvrv endpoint
    def get_mvrv(self, start_ts=None, end_ts=None) -> Dict[str, Any]:
        """Get the Market Value to Realized Value ratio."""
        return self.get_metric("mvrv", start_ts, end_ts)
    
    def get_transaction_fees(self, start_ts=None, end_ts=None) -> Dict[str, Any]:
        """Get the total transaction fees in BTC."""
        return self.get_metric("transaction_fees", start_ts, end_ts)
    
    def get_mempool_size(self, start_ts=None, end_ts=None) -> Dict[str, Any]:
        """Get the size of the mempool in bytes."""
        return self.get_metric("mempool_size", start_ts, end_ts, timespan="1week")
    
    def get_hash_rate(self, start_ts=None, end_ts=None) -> Dict[str, Any]:
        """Get the estimated network hash rate."""
        return self.get_metric("hash_rate", start_ts, end_ts)
    
    def get_difficulty(self, start_ts=None, end_ts=None) -> Dict[str, Any]:
        """Get the network difficulty."""
        return self.get_metric("difficulty", start_ts, end_ts)
    
    def get_utxo_set_size(self, start_ts=None, end_ts=None) -> Dict[str, Any]:
        """Get the UTXO set size."""
        return self.get_metric("utxo_set_size", start_ts, end_ts)
    
    def fetch_all_metrics(self, start_ts=None, end_ts=None) -> Dict[str, Dict[str, Any]]:
        """
        Fetch all available metrics in a single batch.
        """
        results = {}
        for metric_name in self.METRIC_MAPPING.keys():
            try:
                results[metric_name] = self.get_metric(metric_name, start_ts, end_ts)
            except Exception as e:
                logger.error(f"Error fetching metric {metric_name}: {e}")
                results[metric_name] = {"error": str(e)}
        
        return results
    
    def save_metrics_to_file(self, metrics_data: Dict[str, Dict[str, Any]], filename: str) -> None:
        """
        Save metrics data to a JSON file.
        """
        with open(filename, 'w') as f:
            json.dump(metrics_data, f, indent=2)
        
        logger.info(f"Saved metrics data to {filename}")
    
    def metrics_to_dataframe(self, metric_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Convert metric data to a pandas DataFrame.
        """
        if "values" not in metric_data:
            raise ValueError("Invalid metric data format")
        
        # Extract values
        values = metric_data["values"]
        
        # Convert to DataFrame
        df = pd.DataFrame(values)
        
        # Convert timestamps to datetime
        df["timestamp"] = pd.to_datetime(df["x"], unit="s")
        
        # Rename columns
        df = df.rename(columns={"y": metric_data.get("name", "value")})
        
        # Add metadata
        df["unit"] = metric_data.get("unit", "")
        df["description"] = metric_data.get("description", "")
        
        return df
