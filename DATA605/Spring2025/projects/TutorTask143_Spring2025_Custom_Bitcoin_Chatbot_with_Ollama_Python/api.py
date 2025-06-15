import yfinance as yf
from datetime import datetime, timedelta
import time
import datetime
import requests
import pandas as pd
import logging
import json
import re
import os
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import os
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

from tenacity import retry, wait_exponential, stop_after_attempt

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (pd.Timestamp, datetime.datetime, datetime.date)):
            return obj.isoformat()
        return super().default(obj)

# Setup logging
logger = logging.getLogger(__name__)

# Configuration
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
NEWS_API_KEY = "e702ca9925ed4201a7e7818f55a1b806"  # Replace with your News API key
NEWS_API_URL = "https://newsapi.org/v2/everything"
COINGECKO_RATE_LIMIT_WAIT = 6  # seconds between API calls
CACHE_DIR = Path("cache")
CACHE_EXPIRY = {
    "prices": 300,  # 5 minutes
    "historical": 86400,  # 24 hour
    "market": 1800,  # 30 minutes
    "news": 1800  # 30 minutes
}

# Create cache directory if it doesn't exist
CACHE_DIR.mkdir(exist_ok=True)

class DateTimeDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
        
    def object_hook(self, obj):
        for key, value in obj.items():
            if isinstance(value, str) and re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', value):
                try:
                    obj[key] = pd.to_datetime(value)
                except:
                    pass
        return obj



class CoinGeckoAPI:
    @staticmethod
    def _get_cache_path(cache_type: str, identifier: str) -> Path:
        """Generate a cache file path."""
        return CACHE_DIR / f"{cache_type}_{identifier}.json"
    
    @staticmethod
    def _read_cache(cache_path: Path, expiry_seconds: int) -> Optional[Dict]:
        """Read data from cache if it exists and is not expired."""
        if not cache_path.exists():
            return None
            
        # Check if cache is expired
        file_age = time.time() - cache_path.stat().st_mtime
        if file_age > expiry_seconds:
            logger.debug(f"Cache expired: {cache_path}")
            return None
            
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f, cls=DateTimeDecoder)
                
                # ADDED: Convert date strings back to datetime objects if this is historical data
                if "historical" in cache_path.name and isinstance(data, list):
                    for record in data:
                        if "date" in record and isinstance(record["date"], str):
                            record["date"] = pd.to_datetime(record["date"])
                
                return data
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Error reading cache {cache_path}: {e}")
            return None
    
    @staticmethod
    def _write_cache(cache_path: Path, data: Any) -> bool:
        """Write data to cache."""
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f, cls=DateTimeEncoder)
            return True
        except (IOError, TypeError) as e:
            logger.warning(f"Error writing to cache {cache_path}: {e}")
            return False
        
    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), stop=stop_after_attempt(3))
    def fetch_realtime_data(self, coins=["bitcoin"]):
        # Create cache identifier
        cache_id = "_".join(sorted(coins))
        cache_path = self._get_cache_path("prices", cache_id)
        
        # Try to get from cache first
        cached_data = self._read_cache(cache_path, CACHE_EXPIRY["prices"])
        if cached_data:
            logger.info(f"Using cached price data for {', '.join(coins)}")
            return cached_data
            
        # If not in cache or expired, fetch from API
        coins_str = ",".join(coins)
        response = requests.get(
            f"{COINGECKO_API_URL}/simple/price?ids={coins_str}&vs_currencies=usd&include_market_cap=true&include_24hr_change=true"
        )
        response.raise_for_status()
        data = response.json()
        
        # Validate Bitcoin data
        if 'bitcoin' not in data:
            raise ValueError("Missing Bitcoin in API response")
            
        # Cache the result
        self._write_cache(cache_path, data)
        
        return data
    @classmethod
    def fetch_historical_data_coingecko(cls, coin="bitcoin", days=365):
        """Fetch historical data using CoinGecko API"""
        cache_id = f"{coin}_historical_coingecko_{days}d"
        cache_path = cls._get_cache_path("historical", cache_id)
        
        cached_data = cls._read_cache(cache_path, CACHE_EXPIRY["historical"])
        if cached_data:
            logger.info(f"Using cached historical data for {coin} from CoinGecko")
            df = pd.DataFrame(cached_data)
            logger.info(f"Loaded {len(df)} records from cache, date range: {df['date'].min()} to {df['date'].max()}")
            return df
        
        try:
            # Build the URL for the CoinGecko API
            url = f"{COINGECKO_API_URL}/coins/{coin}/market_chart"
            params = {
                'vs_currency': 'usd',
                'days': days,
                'interval': 'daily'
            }
            
            logger.info(f"Fetching {days} days of historical data for {coin} from CoinGecko API")
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Process the price data
            price_data = data.get('prices', [])
            if not price_data:
                logger.error(f"No price data returned for {coin}")
                return None
                
            # Convert to DataFrame
            df = pd.DataFrame(price_data, columns=['timestamp', 'price'])
            df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.drop('timestamp', axis=1)
            
            # Add other data if available
            if 'market_caps' in data:
                market_caps = pd.DataFrame(data['market_caps'], columns=['timestamp', 'market_cap'])
                df['market_cap'] = market_caps['market_cap']
                
            if 'total_volumes' in data:
                volumes = pd.DataFrame(data['total_volumes'], columns=['timestamp', 'volume'])
                df['volume'] = volumes['volume']
                
            # Add OHLC columns (all equal to price since we only get daily prices)
            df['open'] = df['price']
            df['high'] = df['price']
            df['low'] = df['price']
            df['close'] = df['price']
            
            # Sort by date
            df = df.sort_values('date').reset_index(drop=True)
            
            logger.info(f"Retrieved {len(df)} records from CoinGecko from {df['date'].min()} to {df['date'].max()}")
            
            # Cache results
            cls._write_cache(cache_path, df.to_dict(orient='records'))
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching CoinGecko historical data: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return None

     
    @classmethod
    def fetch_historical_data_yf(cls, coin="bitcoin", years=15):
        """Fetch 15 years of historical OHLC data using yFinance"""
        cache_id = f"{coin}_historical_{years}y"
        cache_path = cls._get_cache_path("historical", cache_id)
        
        cached_data = cls._read_cache(cache_path, CACHE_EXPIRY["historical"])
        if cached_data:
            logger.info(f"Using cached historical data for {coin}")
            df = pd.DataFrame(cached_data)
            logger.info(f"Loaded {len(df)} records from cache, date range: {df['date'].min()} to {df['date'].max()}")
            return df
        
        try:
            # Map coin name to yfinance ticker symbol
            ticker_map = {
                "bitcoin": "BTC-USD",
                # Add more mappings as needed
            }
            ticker_symbol = ticker_map.get(coin.lower(), f"{coin.upper()}-USD")
            logger.info(f"Fetching data for {coin} using ticker {ticker_symbol}")
            
            # Calculate date range
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=years*365)
            
            # Fetch data from yFinance
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval="1d",
                auto_adjust=True
            ).reset_index()  # This is the critical fix!
            
            # Verify data was actually returned
            if hist is None or hist.empty:
                logger.error(f"yFinance returned empty data for {coin}")
                return None
                
            # Convert to standard format
            hist = hist[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
            hist.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
            hist['date'] = pd.to_datetime(hist['date'])
            hist['price'] = hist['close']
            
            logger.info(f"Retrieved {len(hist)} records from {hist['date'].min()} to {hist['date'].max()}")
            
            # Cache results
            cls._write_cache(cache_path, hist.to_dict(orient='records'))
            if 'price' not in hist.columns:
                hist['price'] = hist['close']

            return hist
        
        except Exception as e:
            logger.error(f"Error fetching yFinance data: {e}")
            import traceback
            logger.error(traceback.format_exc())  # Add stack trace for better debugging
            return None



    # Keep existing real-time methods
    @classmethod
    def fetch_crypto_prices(cls, coins=["bitcoin"]) -> Dict:
        """Legacy method that calls fetch_realtime_data for backward compatibility."""
        instance = cls()  # Create an instance first
        return instance.fetch_realtime_data(coins)
    
    @classmethod
    def fetch_market_data(cls, coins=["bitcoin"]) -> Dict:
        """Fetch detailed market data for cryptocurrencies with caching."""
        market_data = {}
        
        for coin in coins:
            cache_id = coin
            cache_path = cls._get_cache_path("market", cache_id)
            
            # Try to get from cache first
            cached_data = cls._read_cache(cache_path, CACHE_EXPIRY["market"])
            if cached_data:
                logger.info(f"Using cached market data for {coin}")
                market_data[coin] = cached_data
                continue
                
            # If not in cache or expired, fetch from API
            try:
                response = requests.get(f"{COINGECKO_API_URL}/coins/{coin}", timeout=10)
                response.raise_for_status()
                coin_data = response.json()
                
                # Cache the result
                cls._write_cache(cache_path, coin_data)
                
                market_data[coin] = coin_data
                # Increased delay to respect API rate limits
                time.sleep(COINGECKO_RATE_LIMIT_WAIT)
            except requests.RequestException as e:
                logger.error(f"Error fetching market data for {coin}: {e}")
                # Continue with other coins even if one fails
                continue
                
        logger.info(f"Successfully fetched market data for {len(market_data)} coins")
        return market_data

class NewsAPI:
    """Handles all NewsAPI interactions with caching."""
    
    @staticmethod
    def fetch_crypto_news(coins: list[str], days: int = 3, items: int = 20) -> list[dict]:
        """Fetch cryptocurrency news with proper parameter handling and caching."""
        cache_id = f"{'_'.join(sorted(coins))}_{days}_{items}"
        cache_path = CoinGeckoAPI._get_cache_path("news", cache_id)
        
        # Try to get from cache first
        cached_data = CoinGeckoAPI._read_cache(cache_path, CACHE_EXPIRY["news"])
        if cached_data:
            logger.info(f"Using cached news data for {', '.join(coins)}")
            return cached_data
        
        # If not in cache or expired, fetch from API
        try:
            from_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
            query_terms = [f'"{coin}"' for coin in coins]
            
            params = {
                'q': f"cryptocurrency AND ({' OR '.join(query_terms)})",
                'from': from_date,
                'sortBy': 'relevancy',
                'pageSize': items,
                'language': 'en',
                'apiKey': NEWS_API_KEY
            }
            
            response = requests.get(NEWS_API_URL, params=params, timeout=10)
            response.raise_for_status()
            news_data = response.json().get('articles', [])
            
            # Cache the result
            CoinGeckoAPI._write_cache(cache_path, news_data)
            
            logger.info(f"Successfully fetched {len(news_data)} news articles")
            return news_data
        
        except requests.RequestException as e:
            logger.error(f"NewsAPI error: {str(e)}")
            
            # If we have cached data, return it even if expired
            if cached_data:
                logger.warning("Using expired cached news data due to API error")
                return cached_data
            return []