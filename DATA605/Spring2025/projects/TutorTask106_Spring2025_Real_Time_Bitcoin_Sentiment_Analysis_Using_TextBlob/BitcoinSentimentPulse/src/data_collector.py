import pandas as pd
import numpy as np
import datetime
import requests
import yfinance as yf
from typing import Optional, Dict, Any, List, Tuple
import time
import logging

logger = logging.getLogger(__name__)

class DataCollector:
    """
    Class responsible for collecting Bitcoin price data from various sources.
    
    Attributes:
        source (str): The source for data collection ('coingecko' or 'yfinance')
        api_endpoint (str): The API endpoint for CoinGecko
    """
    
    def __init__(self, source: str = 'coingecko'):
        """
        Initialize the DataCollector with the specified data source.
        
        Args:
            source (str): The source for data collection. Options: 'coingecko', 'yfinance'.
        """
        self.source = source.lower()
        self.api_endpoint = "https://api.coingecko.com/api/v3"
    
    def get_historical_data(self, period: str = '90d') -> pd.DataFrame:
        """
        Retrieve historical Bitcoin price data for the specified period.
        
        Args:
            period (str): Time period for historical data. 
                          Options: '7d', '30d', '90d', '180d', '365d', 'max'
        
        Returns:
            pd.DataFrame: DataFrame with historical price data
        """
        if self.source == 'coingecko':
            return self._get_data_from_coingecko(period)
        elif self.source == 'yfinance':
            return self._get_data_from_yfinance(period)
        else:
            raise ValueError(f"Unsupported data source: {self.source}")
    
    def _get_data_from_coingecko(self, period: str) -> pd.DataFrame:
        """
        Retrieve Bitcoin price data from CoinGecko API.
        
        Args:
            period (str): Time period for historical data
            
        Returns:
            pd.DataFrame: DataFrame with historical price data
        """
        # Map period string to days
        period_days = {
            '7d': 7,
            '30d': 30,
            '90d': 90,
            '180d': 180,
            '365d': 365,
            'max': 'max'
        }
        
        # Determine days parameter
        days = period_days.get(period, 90)
        
        # For 'max' history, we need to use a different endpoint
        if days == 'max':
            endpoint = f"{self.api_endpoint}/coins/bitcoin/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': 'max',
                'interval': 'daily'
            }
        else:
            endpoint = f"{self.api_endpoint}/coins/bitcoin/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily'
            }
        
        try:
            # Make API request with exponential backoff
            max_retries = 5
            retry_delay = 1
            
            for attempt in range(max_retries):
                response = requests.get(endpoint, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    break
                elif response.status_code == 429:  # Rate limit exceeded
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        raise Exception(f"Rate limit exceeded after {max_retries} attempts")
                else:
                    raise Exception(f"API request failed with status code {response.status_code}: {response.text}")
            
            # Process price data
            prices = data.get('prices', [])
            
            if not prices:
                raise ValueError("No price data returned from CoinGecko API")
            
            # Convert to DataFrame
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            
            # Convert timestamp (milliseconds) to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Set timestamp as index
            df = df.set_index('timestamp')
            
            # Sort by date
            df = df.sort_index()
            
            return df
            
        except Exception as e:
            raise Exception(f"Error fetching data from CoinGecko: {str(e)}")
    
    def _get_data_from_yfinance(self, period: str) -> pd.DataFrame:
        """
        Retrieve Bitcoin price data from Yahoo Finance.
        
        Args:
            period (str): Time period for historical data
            
        Returns:
            pd.DataFrame: DataFrame with historical price data
        """
        try:
            # Map to yfinance period format
            yf_period = {
                '7d': '7d',
                '30d': '1mo',
                '90d': '3mo',
                '180d': '6mo',
                '365d': '1y',
                'max': 'max'
            }.get(period, '3mo')
            
            # Get data from yfinance
            btc_data = yf.download('BTC-USD', period=yf_period, interval='1d')
            
            if btc_data.empty:
                logger.warning("No data returned from Yahoo Finance, falling back to CoinGecko")
                return self._get_data_from_coingecko(period)
            
            # Select close price and rename
            df = btc_data[['Close']].copy()
            df.rename(columns={'Close': 'price'}, inplace=True)
            
            # Add technical indicators
            df = self.add_technical_indicators(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data from Yahoo Finance: {str(e)}")
            logger.info("Falling back to CoinGecko")
            return self._get_data_from_coingecko(period)
            
    def get_real_time_price(self) -> float:
        """
        Get the current real-time price of Bitcoin.
        
        Returns:
            float: The current Bitcoin price in USD
        """
        if self.source == 'coingecko':
            try:
                endpoint = f"{self.api_endpoint}/simple/price"
                params = {
                    'ids': 'bitcoin',
                    'vs_currencies': 'usd'
                }
                
                response = requests.get(endpoint, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    return data['bitcoin']['usd']
                else:
                    raise Exception(f"API request failed with status code {response.status_code}")
                    
            except Exception as e:
                raise Exception(f"Error fetching real-time price from CoinGecko: {str(e)}")
                
        elif self.source == 'yfinance':
            try:
                ticker = yf.Ticker('BTC-USD')
                todays_data = ticker.history(period='1d')
                
                if todays_data.empty:
                    raise ValueError("No data returned from Yahoo Finance")
                    
                return todays_data['Close'].iloc[-1]
                
            except Exception as e:
                raise Exception(f"Error fetching real-time price from Yahoo Finance: {str(e)}")
                
        else:
            raise ValueError(f"Unsupported data source: {self.source}")

    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add technical indicators to the price data.
        
        Args:
            df (pd.DataFrame): DataFrame with price data
            
        Returns:
            pd.DataFrame: DataFrame with added technical indicators
        """
        try:
            # Calculate RSI
            delta = df['price'].diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            rs = avg_gain / avg_loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # Calculate MACD
            exp1 = df['price'].ewm(span=12, adjust=False).mean()
            exp2 = df['price'].ewm(span=26, adjust=False).mean()
            df['macd'] = exp1 - exp2
            df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['macd_hist'] = df['macd'] - df['macd_signal']
            
            # Calculate Bollinger Bands
            df['bb_middle'] = df['price'].rolling(window=20).mean()
            df['bb_std'] = df['price'].rolling(window=20).std()
            df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
            df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)
            
            # Fill NaN values
            df.fillna(method='bfill', inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {str(e)}")
            return df  # Return original DataFrame if calculation fails

    def get_data_from_coingecko(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Get Bitcoin price data from CoinGecko.
        
        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            
        Returns:
            pd.DataFrame: DataFrame with Bitcoin price data
        """
        try:
            # Convert dates to datetime
            start = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            
            # Calculate days between dates
            days = (end - start).days
            
            # Get data from CoinGecko
            url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': str(days),
                'interval': 'daily'
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise exception for bad status codes
            
            data = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Filter for the exact date range
            df = df[start:end]
            
            if df.empty:
                raise ValueError("No data returned from CoinGecko")
            
            # Add technical indicators
            df = self.add_technical_indicators(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data from CoinGecko: {str(e)}")
            raise Exception(f"Failed to fetch data from both Yahoo Finance and CoinGecko: {str(e)}")
