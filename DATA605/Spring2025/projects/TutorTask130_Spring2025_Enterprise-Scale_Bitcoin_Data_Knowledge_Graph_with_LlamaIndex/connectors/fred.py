import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Union
import logging
import json
from fredapi import Fred
import os
from dotenv import load_dotenv

load_dotenv("devops/env/default.env")
FRED_API_KEY = os.getenv('FRED_API_KEY')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FredApiConnector:
    """
    Connector for the FRED (Federal Reserve Economic Data) API to fetch macroeconomic indicators.
    """
    
    # Mapping of our metric names to FRED series IDs
    METRIC_MAPPING = {
        "federal_funds_rate": "FEDFUNDS",  # Federal Funds Effective Rate
        "cpi": "CPIAUCSL",               # Consumer Price Index for All Urban Consumers
        "real_gdp_growth": "A191RL1Q225SBEA", 
        "unemployment_rate": "UNRATE",
        "sp500": "SP500",                
        "dollar_index": "DTWEXBGS",      # Trade Weighted U.S. Dollar Index: Broad, Goods
        "m2_money_supply": "M2SL"        # M2 Money Stock
    }
    
    def __init__(self, api_key: str = FRED_API_KEY, rate_limit_delay: float = 2.0):
        """
        Initialize the FredApiConnector.

        """
        self.api_key = api_key
        self.rate_limit_delay = rate_limit_delay
        self.fred = Fred(api_key=api_key)
    
    def _format_date(self, ts: Optional[Union[int, datetime, str]]) -> Optional[str]:
        """
        Format a timestamp to YYYY-MM-DD format for FRED API.
        """
        if ts is None:
            return None
        
        if isinstance(ts, int):
            ts = datetime.fromtimestamp(ts)
        
        if isinstance(ts, datetime):
            return ts.strftime('%Y-%m-%d')
        
        return ts  # Assume it's already in the correct format
    
    def get_metric(
        self, 
        metric_name: str, 
        start_ts: Optional[Union[int, datetime, str]] = None,
        end_ts: Optional[Union[int, datetime, str]] = None,
    ) -> pd.Series:
        """
        Get a metric from the FRED API.
        """
        if metric_name not in self.METRIC_MAPPING:
            raise ValueError(f"Unknown metric: {metric_name}. Available metrics: {list(self.METRIC_MAPPING.keys())}")
        
        series_id = self.METRIC_MAPPING[metric_name]
        
        # Format dates for FRED API
        start_date = self._format_date(start_ts)
        end_date = self._format_date(end_ts)
        
        logger.info(f"Fetching {metric_name} (series_id: {series_id}) from {start_date} to {end_date}")
        
        try:
            # Get data from FRED API
            data = self.fred.get_series(
                series_id, 
                observation_start=start_date,
                observation_end=end_date,
            )
            
            # Add a delay to respect rate limits
            time.sleep(self.rate_limit_delay)
            
            return data
        except Exception as e:
            logger.error(f"Error fetching {metric_name} from FRED: {e}")
            raise
    
    def series_to_json(self, series: pd.Series) -> Dict[str, Any]:
        """
        Convert a pandas Series to a JSON-compatible dictionary.
        """
        # Reset index to get dates as a column
        df = series.reset_index()
        
        # Rename columns
        df.columns = ['date', 'value']
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        records = df.to_dict(orient='records')
        
        return {
            'indicator': series.name or '',
            'values': records,
            'count': len(records)
        }
    
    def get_federal_funds_rate(self, start_ts=None, end_ts=None) -> Dict[str, Any]:
        """Get the Federal Funds Rate."""
        data = self.get_metric("federal_funds_rate", start_ts, end_ts)
        data.name = "Federal Funds Rate"
        return self.series_to_json(data)
    
    def get_cpi(self, start_ts=None, end_ts=None) -> Dict[str, Any]:
        """Get the Consumer Price Index (CPI)."""
        data = self.get_metric("cpi", start_ts, end_ts)
        data.name = "Consumer Price Index"
        return self.series_to_json(data)
    
    def get_real_gdp_growth(self, start_ts=None, end_ts=None) -> Dict[str, Any]:
        """Get the Real GDP Growth Rate."""
        data = self.get_metric("real_gdp_growth", start_ts, end_ts)
        data.name = "Real GDP Growth Rate"
        return self.series_to_json(data)
    
    def get_unemployment_rate(self, start_ts=None, end_ts=None) -> Dict[str, Any]:
        """Get the Unemployment Rate."""
        data = self.get_metric("unemployment_rate", start_ts, end_ts)
        data.name = "Unemployment Rate"
        return self.series_to_json(data)
    
    def get_sp500(self, start_ts=None, end_ts=None) -> Dict[str, Any]:
        """Get the S&P 500 Index."""
        data = self.get_metric("sp500", start_ts, end_ts)
        data.name = "S&P 500 Index"
        return self.series_to_json(data)
    
    def get_dollar_index(self, start_ts=None, end_ts=None) -> Dict[str, Any]:
        """Get the Trade Weighted US Dollar Index."""
        data = self.get_metric("dollar_index", start_ts, end_ts)
        data.name = "Trade Weighted US Dollar Index"
        return self.series_to_json(data)
    
    def get_m2_money_supply(self, start_ts=None, end_ts=None) -> Dict[str, Any]:
        """Get the M2 Money Supply."""
        data = self.get_metric("m2_money_supply", start_ts, end_ts)
        data.name = "M2 Money Supply"
        return self.series_to_json(data)
    
    def fetch_all_metrics(self, start_ts=None, end_ts=None) -> Dict[str, Dict[str, Any]]:
        """
        Fetch all available metrics in a single batch.
        """
        results = {}
        for metric_name in self.METRIC_MAPPING.keys():
            try:
                # Get the corresponding method
                method_name = f"get_{metric_name}"
                method = getattr(self, method_name)
                
                # Call the method
                results[metric_name] = method(start_ts, end_ts)
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
        
        # Convert date strings to datetime
        df["date"] = pd.to_datetime(df["date"])
        
        # Rename columns if needed
        if "value" in df.columns:
            df = df.rename(columns={"value": metric_data.get("unit", "value")})
        
        return df