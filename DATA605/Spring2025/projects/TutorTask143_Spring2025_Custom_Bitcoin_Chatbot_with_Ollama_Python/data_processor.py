"""
Enhanced data processing module for cryptocurrency data.
Handles data collection, processing, and formatting for RAG system with improved NLP capabilities.
"""

import datetime
import logging
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
from langchain.schema import Document
import re
from dateutil import parser
from collections import defaultdict
from sentiment_analyzer import CryptoSentimentAnalyzer
from technical_indicators import TechnicalIndicators

from api import CoinGeckoAPI, NewsAPI

# Configuration
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
NEWS_API_KEY = "e702ca9925ed4201a7e7818f55a1b806"  # Replace with your News API key
NEWS_API_URL = "https://newsapi.org/v2/everything"
OLLAMA_MODEL = "mistral"  # or another model you have pulled in Ollama
VECTOR_DB_PATH = "faiss_index"
UPDATE_INTERVAL = 15  # minutes
# Added API rate limit constants
COINGECKO_RATE_LIMIT_WAIT = 6  # seconds between API calls

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Add handler if none exists
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class CryptoData:
    """Handles collecting and processing cryptocurrency data with enhanced NLP support."""
    
    def __init__(self):
        self.price_data = {}
        self.market_data = {}
        self.news_data = []
        self.historical_data = {}
        self.last_update = None
        self.date_price_lookup = {}  # For quick date-to-price lookups
        self.coin_aliases = {
            "bitcoin": ["btc", "bitcoin", "xbt"],
             
            # Add more as needed
        }
        
        # Initialize API handlers
        self.coingecko_api = CoinGeckoAPI()
        self.news_api = NewsAPI()

        # Initialize sentiment analyzer
        self.sentiment_analyzer = CryptoSentimentAnalyzer()
        
        # Initialize technical indicators
        self.technical_indicators = TechnicalIndicators()
        
        # Store sentiment and technical analysis results
        self.sentiment_results = {}
        self.technical_analysis = {}
    
    def normalize_coin_name(self, coin_name: str) -> str:
        """Convert various coin name formats to standard CoinGecko format."""
        coin_name = coin_name.lower().strip()
        
        # Check if name directly matches a known coin
        if coin_name in self.coin_aliases:
            return coin_name
            
        # Check if name is in aliases
        for standard_name, aliases in self.coin_aliases.items():
            if coin_name in aliases:
                return standard_name
                
        # Return original if no match found
        return coin_name
    
    def update_all_data(self, coins=["bitcoin"]):
        try:
            self.last_update = datetime.datetime.now()
            logger.info(f"Starting data update for coins: {', '.join(coins)}")
            
            normalized_coins = [self.normalize_coin_name(coin) for coin in coins]
            self.price_data = self.coingecko_api.fetch_crypto_prices(normalized_coins)
            
            # Process each coin individually to prevent one failure from affecting others
            for coin in normalized_coins:
                try:
                    data = self.coingecko_api.fetch_historical_data_yf(coin, years=15)
                    if data is not None and not data.empty:
                        self.historical_data[coin] = data
                        logger.info(f"Successfully retrieved historical data for {coin}: {len(data)} records")
                    else:
                        logger.error(f"Failed to retrieve valid historical data for {coin}")
                except Exception as e:
                    logger.error(f"Error fetching historical data for {coin}: {str(e)}")
            
            # Only proceed with coins that have valid data
            valid_coins = [c for c in normalized_coins if c in self.historical_data and 
                        self.historical_data[c] is not None and not self.historical_data[c].empty]
            
            if valid_coins:
                self.verify_historical_data()
                self._build_date_price_lookup()
                logger.info(f"Built date-price lookup for {len(valid_coins)} coins")
                
                # Only update market data and news for valid coins
                self.market_data = self.coingecko_api.fetch_market_data(valid_coins)
                self.news_data = self.news_api.fetch_crypto_news(coins=valid_coins, items=20)
                
                self.update_sentiment_analysis()
                self.update_technical_analysis(valid_coins)
                
                self.last_update = datetime.datetime.now()
                logger.info(f"All data updated at {self.last_update}")
                return True
            else:
                logger.error("No valid historical data available for any coin")
                return False
                
        except Exception as e:
            logger.error(f"Error updating data: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def _save_date_price_lookup(self):
        """Save date-price lookup to disk"""
        import pickle
        with open("date_price_lookup.pkl", "wb") as f:
            pickle.dump(self.date_price_lookup, f)

    def _load_date_price_lookup(self):
        """Load date-price lookup from disk"""
        import pickle
        try:
            with open("date_price_lookup.pkl", "rb") as f:
                self.date_price_lookup = pickle.load(f)
        except FileNotFoundError:
            self.date_price_lookup = defaultdict(dict)
    
    def _build_date_price_lookup(self):
        """Build a lookup dictionary for quick date-to-price queries."""
        self.date_price_lookup = defaultdict(dict)
        
        for coin, df in self.historical_data.items():
            if df is None or df.empty:
                logger.warning(f"No data available for date-price lookup for {coin}")
                continue
                
            try:
                # Ensure date column exists and is in datetime format
                if 'date' not in df.columns:
                    logger.warning(f"No 'date' column in data for {coin}")
                    logger.warning(f"Available columns: {df.columns.tolist()}")
                    continue
                    
                # Convert to datetime if not already
                if not pd.api.types.is_datetime64_any_dtype(df['date']):
                    df['date'] = pd.to_datetime(df['date'])
                    
                # Add price column if missing
                if 'price' not in df.columns and 'close' in df.columns:
                    df['price'] = df['close']
                elif 'price' not in df.columns:
                    logger.warning(f"No 'price' or 'close' column in data for {coin}")
                    continue
                    
                # Log the date range being processed
                min_date = df['date'].min()
                max_date = df['date'].max()
                logger.info(f"Building date-price lookup for {coin} from {min_date} to {max_date}")
                
                # Build the lookup dictionary with proper error handling
                count = 0
                for _, row in df.iterrows():
                    try:
                        # Fix: Handle DataFrame index and date conversion properly
                        if isinstance(row['date'], pd.Timestamp):
                            date_str = row['date'].strftime('%Y-%m-%d')
                        else:
                            date_str = pd.to_datetime(row['date']).strftime('%Y-%m-%d')
                        self.date_price_lookup[coin][date_str] = float(row['price'])
                        count += 1
                    except Exception as e:
                        logger.error(f"Error processing row {_} for {coin}: {str(e)}")
                        
                logger.info(f"Added {count} date-price entries for {coin}")
            except Exception as e:
                logger.error(f"Error building date-price lookup for {coin}: {str(e)}")
                logger.error(f"Available columns: {df.columns.tolist()}")

    
    # In CryptoData class

    def get_price_for_date(self, coin: str, date_str: str) -> Optional[float]:
        """Get price for a specific coin on a specific date with improved date handling."""
        coin = self.normalize_coin_name(coin)
        
        try:
            # First, make sure we have data for this coin
            if coin not in self.date_price_lookup:
                logger.warning(f"No price data available for {coin}")
                return None
                
            # Try to parse the date to a standard format
            try:
                target_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                # If the standard format fails, try with dateutil parser
                try:
                    target_date = parser.parse(date_str)
                except Exception as e:
                    logger.error(f"Could not parse date: {date_str}, error: {str(e)}")
                    return None
                    
            formatted_date_str = target_date.strftime('%Y-%m-%d')
            
            # Log what we're looking for
            logger.debug(f"Looking up price for {coin} on {formatted_date_str}")
            
            # Direct match
            if formatted_date_str in self.date_price_lookup[coin]:
                price = self.date_price_lookup[coin][formatted_date_str]
                return price
                
            # Find closest available date if no direct match
            available_dates = sorted(
                datetime.datetime.strptime(d, "%Y-%m-%d").date()
                for d in self.date_price_lookup[coin].keys()
            )
            
            if not available_dates:
                return None
                
            target_date_only = target_date.date()
            closest_date = min(available_dates, key=lambda d: abs(d - target_date_only))
            closest_date_str = closest_date.strftime("%Y-%m-%d")
            
            return self.date_price_lookup[coin].get(closest_date_str)
            
        except Exception as e:
            logger.error(f"Error in date fallback for {coin} on {date_str}: {str(e)}")
            return None


    
    def get_formatted_data(self) -> List[Document]:
        """Format all data into documents for the vector store with enhanced NLP support."""
        documents = []
        
        # Format price data
        if self.price_data:
            for coin, data in self.price_data.items():
                content = f"Price data for {coin} as of {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:\n"
                content += f"Price: ${data.get('usd', 'N/A')}\n"
                content += f"Market Cap: ${data.get('usd_market_cap', 'N/A')}\n"
                content += f"24h Volume: ${data.get('usd_24h_vol', 'N/A')}\n"
                content += f"24h Change: {data.get('usd_24h_change', 'N/A')}%\n"
                
                # Add natural language summary for better RAG retrieval
                nl_summary = f"The current price of {coin} is ${data.get('usd', 'N/A')}. "
                if 'usd_24h_change' in data and data['usd_24h_change'] is not None:
                    change = data['usd_24h_change']
                    if change > 0:
                        nl_summary += f"It has increased by {change:.2f}% in the last 24 hours. "
                    elif change < 0:
                        nl_summary += f"It has decreased by {abs(change):.2f}% in the last 24 hours. "
                    else:
                        nl_summary += f"Its price has remained stable in the last 24 hours. "
                
                content += f"\nSummary: {nl_summary}\n"
                
                documents.append(Document(
                    page_content=content,
                    metadata={
                        "source": "coingecko_price", 
                        "coin": coin, 
                        "timestamp": datetime.datetime.now().isoformat(),
                        "type": "price_data",
                        "current_price": data.get('usd', 'N/A')
                    }
                ))
                
        # Format historical data with comprehensive analysis
        if self.historical_data:
            for coin, df in self.historical_data.items():
                if df is None or df.empty:
                    continue
                
                # Create a summary document of historical data
                content = f"Historical price analysis for {coin} as of {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:\n"
                
                # Latest price and change
                latest_price = df['price'].iloc[-1] if 'price' in df.columns else "N/A"
                content += f"Latest Price: ${latest_price}\n"
                
                # Historical statistics
                if 'price' in df.columns:
                    content += f"Year High: ${df['price'].max()}\n"
                    content += f"Year Low: ${df['price'].min()}\n"
                    content += f"Year Average: ${df['price'].mean():.2f}\n"
                    
                    # Calculate yearly change
                    if len(df) > 1:
                        yearly_change = ((df['price'].iloc[-1] / df['price'].iloc[0]) - 1) * 100
                        content += f"Yearly Change: {yearly_change:.2f}%\n"
                
                # Volatility
                if 'price' in df.columns and len(df) > 1:
                    volatility = df['price'].pct_change().std() * 100
                    content += f"Daily Volatility (StdDev): {volatility:.2f}%\n"
                
                # Last 30 days trend
                if len(df) >= 30:
                    last_30d = df.iloc[-30:]
                    last_30d_change = ((last_30d['price'].iloc[-1] / last_30d['price'].iloc[0]) - 1) * 100
                    content += f"Last 30 Days Trend: {last_30d_change:.2f}%\n"
                
                # Add quarterly breakdowns
                if len(df) >= 90:
                    quarters = min(4, len(df) // 90)  # Up to 4 quarters if we have the data
                    for i in range(quarters):
                        start_idx = -(i+1)*90
                        end_idx = -i*90 if i > 0 else None
                        quarter_data = df.iloc[start_idx:end_idx]
                        q_start_price = quarter_data['price'].iloc[0]
                        q_end_price = quarter_data['price'].iloc[-1]
                        q_change = ((q_end_price / q_start_price) - 1) * 100
                        
                        quarter_name = f"Q{4-i}" if i < 4 else f"Earlier"
                        content += f"{quarter_name} Performance: {q_change:.2f}%\n"
                
                # Add natural language summary for better RAG retrieval
                nl_summary = f"{coin} has had a {yearly_change:.2f}% change over the past year. "
                if yearly_change > 0:
                    nl_summary += f"It has been a good year for {coin} with prices increasing from ${df['price'].iloc[0]:.2f} to ${latest_price:.2f}. "
                else:
                    nl_summary += f"It has been a challenging year for {coin} with prices dropping from ${df['price'].iloc[0]:.2f} to ${latest_price:.2f}. "
                
                if last_30d_change > 0:
                    nl_summary += f"The trend over the last 30 days has been positive with a {last_30d_change:.2f}% increase. "
                else:
                    nl_summary += f"The trend over the last 30 days has been negative with a {abs(last_30d_change):.2f}% decrease. "
                
                content += f"\nSummary: {nl_summary}\n"
                
                # Add a special section for date-based price lookup
                content += "\nHistorical Daily Prices (for date-based queries):\n"
                # List the last 10 days as examples
                recent_dates = df.iloc[-10:].copy()
                for _, row in recent_dates.iterrows():
                    if 'date' in row and 'price' in row:
                        date_str = row['date'].strftime('%Y-%m-%d') if hasattr(row['date'], 'strftime') else str(row['date'])
                        content += f"{date_str}: ${row['price']:.2f}\n"
                
                # Add the document
                documents.append(Document(
                    page_content=content,
                    metadata={
                        "source": "historical_analysis", 
                        "coin": coin, 
                        "timestamp": datetime.datetime.now().isoformat(),
                        "data_period": "365 days",
                        "type": "historical_data"
                    }
                ))
                
                # Create separate documents for different time frames
                # Last 7 days
                if len(df) >= 7:
                    last_7d = df.iloc[-7:]
                    content = f"Last 7 days analysis for {coin}:\n"
                    content += f"7-day Change: {((last_7d['price'].iloc[-1] / last_7d['price'].iloc[0]) - 1) * 100:.2f}%\n"
                    content += f"7-day High: ${last_7d['price'].max():.2f}\n"
                    content += f"7-day Low: ${last_7d['price'].min():.2f}\n"
                    if 'volume' in df.columns:
                        content += f"Average Daily Volume: ${last_7d['volume'].mean():.2f}\n"
                    
                    # Add specific date prices for the last 7 days
                    content += "\nDaily Prices (last 7 days):\n"
                    for _, row in last_7d.iterrows():
                        if 'date' in row and 'price' in row:
                            date_str = row['date'].strftime('%Y-%m-%d') if hasattr(row['date'], 'strftime') else str(row['date'])
                            content += f"{date_str}: ${row['price']:.2f}\n"
                    
                    documents.append(Document(
                        page_content=content,
                        metadata={
                            "source": "historical_analysis", 
                            "coin": coin, 
                            "timestamp": datetime.datetime.now().isoformat(),
                            "data_period": "7 days",
                            "type": "short_term_data"
                        }
                    ))
                
                # Last 30 days
                if len(df) >= 30:
                    last_30d = df.iloc[-30:]
                    content = f"Last 30 days analysis for {coin}:\n"
                    content += f"30-day Change: {((last_30d['price'].iloc[-1] / last_30d['price'].iloc[0]) - 1) * 100:.2f}%\n"
                    content += f"30-day High: ${last_30d['price'].max():.2f}\n"
                    content += f"30-day Low: ${last_30d['price'].min():.2f}\n"
                    if 'volume' in df.columns:
                        content += f"Average Daily Volume: ${last_30d['volume'].mean():.2f}\n"
                    if 'price' in df.columns and len(last_30d) > 1:
                        content += f"30-day Volatility: {last_30d['price'].pct_change().std() * 100:.2f}%\n"
                    
                    # Add weekly average prices for better time-based queries
                    if len(last_30d) >= 28:  # At least 4 weeks
                        content += "\nWeekly Average Prices (last 4 weeks):\n"
                        for i in range(4):
                            start_idx = -(i+1)*7
                            end_idx = -i*7 if i > 0 else None
                            week_data = last_30d.iloc[start_idx:end_idx]
                            week_avg = week_data['price'].mean()
                            week_name = f"Week {i+1}" if i > 0 else "This week"
                            content += f"{week_name}: ${week_avg:.2f}\n"
                    
                    documents.append(Document(
                        page_content=content,
                        metadata={
                            "source": "historical_analysis", 
                            "coin": coin, 
                            "timestamp": datetime.datetime.now().isoformat(),
                            "data_period": "30 days",
                            "type": "medium_term_data"
                        }
                    ))
                
                # Last 90 days
                if len(df) >= 90:
                    last_90d = df.iloc[-90:]
                    content = f"Last 90 days (quarter) analysis for {coin}:\n"
                    content += f"Quarterly Change: {((last_90d['price'].iloc[-1] / last_90d['price'].iloc[0]) - 1) * 100:.2f}%\n"
                    content += f"Quarter High: ${last_90d['price'].max():.2f}\n"
                    content += f"Quarter Low: ${last_90d['price'].min():.2f}\n"
                    
                    # Add any pattern recognition or trend analysis
                    # Calculate simple moving averages
                    if 'price' in last_90d.columns:
                        last_90d.loc[:, 'rolling_7d_avg'] = last_90d['price'].rolling(window=7).mean()
                        last_90d.loc[:, 'rolling_30d_avg'] = last_90d['price'].rolling(window=30).mean()
                        
                        # Simple trend detection using moving averages crossover
                        if last_90d['rolling_7d_avg'].iloc[-1] > last_90d['rolling_30d_avg'].iloc[-1]:
                            content += "Current Trend: Short-term uptrend (7-day MA > 30-day MA)\n"
                        else:
                            content += "Current Trend: Short-term downtrend (7-day MA < 30-day MA)\n"
                    
                    documents.append(Document(
                        page_content=content,
                        metadata={
                            "source": "historical_analysis", 
                            "coin": coin, 
                            "timestamp": datetime.datetime.now().isoformat(),
                            "data_period": "90 days",
                            "type": "quarterly_data"
                        }
                    ))
                    
                # Full year analysis
                if len(df) >= 300:  # Close to a full year
                    content = f"Full year analysis for {coin}:\n"
                    
                    # Calculate monthly returns
                    if len(df) > 30:
                        monthly_returns = []
                        monthly_prices = {}
                        for i in range(min(12, len(df) // 30)):
                            start_idx = -(i+1)*30
                            end_idx = -i*30 if i > 0 else None
                            month_data = df.iloc[start_idx:end_idx]
                            month_return = ((month_data['price'].iloc[-1] / month_data['price'].iloc[0]) - 1) * 100
                            monthly_returns.append(month_return)
                            
                            # Store the monthly average price
                            month_ago = datetime.datetime.now() - datetime.timedelta(days=30*(i+1))
                            month_name = month_ago.strftime('%B %Y')
                            monthly_prices[month_name] = month_data['price'].mean()
                        
                        # Format the monthly returns and prices
                        content += "Monthly Returns (most recent first):\n"
                        for i, ret in enumerate(monthly_returns):
                            month_ago = datetime.datetime.now() - datetime.timedelta(days=30*(i+1))
                            month_name = month_ago.strftime('%B %Y')
                            content += f"{month_name}: {ret:.2f}%\n"
                        
                        content += "\nMonthly Average Prices (most recent first):\n"
                        for month_name, price in monthly_prices.items():
                            content += f"{month_name}: ${price:.2f}\n"
                    
                    # Identify best and worst months
                    if monthly_returns:
                        content += f"Best Monthly Return: {max(monthly_returns):.2f}%\n"
                        content += f"Worst Monthly Return: {min(monthly_returns):.2f}%\n"
                    
                    documents.append(Document(
                        page_content=content,
                        metadata={
                            "source": "historical_analysis", 
                            "coin": coin, 
                            "timestamp": datetime.datetime.now().isoformat(),
                            "data_period": "365 days",
                            "type": "yearly_data"
                        }
                    ))
        
        # Format market data
        if self.market_data:
            for coin, data in self.market_data.items():
                if not data:
                    continue
                    
                content = f"Market data for {coin} ({data.get('symbol', '').upper()}) as of {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:\n"
                
                # Basic information
                content += f"Name: {data.get('name', 'N/A')}\n"
                content += f"Current Price: ${data.get('market_data', {}).get('current_price', {}).get('usd', 'N/A')}\n"
                content += f"Market Cap Rank: {data.get('market_cap_rank', 'N/A')}\n"
                
                # Market data
                market_data = data.get('market_data', {})
                content += f"Market Cap: ${market_data.get('market_cap', {}).get('usd', 'N/A')}\n"
                content += f"Total Volume: ${market_data.get('total_volume', {}).get('usd', 'N/A')}\n"
                content += f"24h High: ${market_data.get('high_24h', {}).get('usd', 'N/A')}\n"
                content += f"24h Low: ${market_data.get('low_24h', {}).get('usd', 'N/A')}\n"
                content += f"Price Change 24h: {market_data.get('price_change_percentage_24h', 'N/A')}%\n"
                content += f"Price Change 7d: {market_data.get('price_change_percentage_7d', 'N/A')}%\n"
                content += f"Price Change 30d: {market_data.get('price_change_percentage_30d', 'N/A')}%\n"
                
                # Added yearly change if available
                if 'price_change_percentage_1y' in market_data:
                    content += f"Price Change 1y: {market_data.get('price_change_percentage_1y', 'N/A')}%\n"
                
                # Developer data if available
                dev_data = data.get('developer_data', {})
                if dev_data:
                    content += f"GitHub Forks: {dev_data.get('forks', 'N/A')}\n"
                    content += f"GitHub Stars: {dev_data.get('stars', 'N/A')}\n"
                    content += f"GitHub Subscribers: {dev_data.get('subscribers', 'N/A')}\n"
                
                # Community data if available
                community_data = data.get('community_data', {})
                if community_data:
                    content += f"Twitter Followers: {community_data.get('twitter_followers', 'N/A')}\n"
                    content += f"Reddit Subscribers: {community_data.get('reddit_subscribers', 'N/A')}\n"
                
                # Add natural language summary
                nl_summary = f"{coin} is currently priced at ${market_data.get('current_price', {}).get('usd', 'N/A')} with a market cap of ${market_data.get('market_cap', {}).get('usd', 'N/A')}. "
                
                price_change_24h = market_data.get('price_change_percentage_24h')
                if price_change_24h is not None:
                    if price_change_24h > 0:
                        nl_summary += f"It has increased by {price_change_24h:.2f}% in the last 24 hours. "
                    elif price_change_24h < 0:
                        nl_summary += f"It has decreased by {abs(price_change_24h):.2f}% in the last 24 hours. "
                    else:
                        nl_summary += f"Its price has remained stable in the last 24 hours. "
                
                price_change_7d = market_data.get('price_change_percentage_7d')
                if price_change_7d is not None:
                    if price_change_7d > 0:
                        nl_summary += f"The 7-day trend is positive with a {price_change_7d:.2f}% increase. "
                    elif price_change_7d < 0:
                        nl_summary += f"The 7-day trend is negative with a {abs(price_change_7d):.2f}% decrease. "
                    else:
                        nl_summary += f"The 7-day trend is stable. "
                
                content += f"\nSummary: {nl_summary}\n"
                
                documents.append(Document(
                    page_content=content,
                    metadata={
                        "source": "coingecko_market", 
                        "coin": coin, 
                        "timestamp": datetime.datetime.now().isoformat(),
                        "price": market_data.get('current_price', {}).get('usd', 'N/A'),
                        "type": "market_data"
                    }
                ))
        

        if self.sentiment_results:
            content = f"Cryptocurrency Market Sentiment Analysis as of {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:\n"
            content += f"Overall Market Sentiment: {self.sentiment_results['overall_sentiment']}\n"
            content += f"Sentiment Score: {self.sentiment_results['score']:.2f}\n"
            content += f"Articles Analyzed: {self.sentiment_results['articles_analyzed']}\n\n"
            
            # Add sentiment trend if available
            trend_data = self.sentiment_analyzer.get_sentiment_trend(days=7)
            if trend_data and 'trend' in trend_data:
                content += f"7-Day Sentiment Trend: {trend_data['trend']}\n"
                content += f"Average 7-Day Score: {trend_data.get('avg_score', 0):.2f}\n\n"
            
            # Add natural language summary
            nl_summary = f"The overall cryptocurrency market sentiment is currently {self.sentiment_results['overall_sentiment']} "
            nl_summary += f"with a sentiment score of {self.sentiment_results['score']:.2f}. "
            
            if trend_data and 'trend' in trend_data:
                nl_summary += f"The sentiment trend over the past 7 days has been {trend_data['trend']}. "
            
            content += f"\nSummary: {nl_summary}\n"
            
            documents.append(Document(
                page_content=content,
                metadata={
                    "source": "sentiment_analysis",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "type": "sentiment_data",
                    "sentiment": self.sentiment_results['overall_sentiment'],
                    "score": self.sentiment_results['score']
                }
            ))
    
        # Add technical analysis documents
        for coin, analysis in self.technical_analysis.items():
            content = f"Technical Analysis for {coin} as of {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:\n"
            
            # RSI
            if 'rsi' in analysis:
                content += f"RSI: {analysis['rsi']:.2f}\n"
                if analysis['rsi'] < 30:
                    content += "RSI indicates oversold conditions (potential buying opportunity)\n"
                elif analysis['rsi'] > 70:
                    content += "RSI indicates overbought conditions (potential selling opportunity)\n"
                else:
                    content += "RSI indicates neutral conditions\n"
            
            # MACD
            if all(k in analysis for k in ['macd_line', 'macd_signal', 'macd_histogram']):
                content += f"MACD Line: {analysis['macd_line']:.2f}\n"
                content += f"MACD Signal: {analysis['macd_signal']:.2f}\n"
                content += f"MACD Histogram: {analysis['macd_histogram']:.2f}\n"
                
                if analysis['macd_line'] > analysis['macd_signal']:
                    content += "MACD is bullish (MACD line above signal line)\n"
                else:
                    content += "MACD is bearish (MACD line below signal line)\n"
            
            # Bollinger Bands
            if all(k in analysis for k in ['bollinger_upper', 'bollinger_middle', 'bollinger_lower']):
                content += f"Bollinger Middle Band: ${analysis['bollinger_middle']:.2f}\n"
                content += f"Bollinger Upper Band: ${analysis['bollinger_upper']:.2f}\n"
                content += f"Bollinger Lower Band: ${analysis['bollinger_lower']:.2f}\n"
                
                price = analysis.get('price', 0)
                if price > analysis['bollinger_upper']:
                    content += "Price is above upper Bollinger Band (potential overbought condition)\n"
                elif price < analysis['bollinger_lower']:
                    content += "Price is below lower Bollinger Band (potential oversold condition)\n"
                else:
                    content += "Price is within Bollinger Bands (normal volatility)\n"
            
            # Overall signal
            content += f"Overall Signal: {analysis.get('signal', 'hold')}\n"
            
            # Add natural language summary
            nl_summary = f"Technical analysis for {coin} shows "
            
            if 'rsi' in analysis:
                nl_summary += f"an RSI of {analysis['rsi']:.2f}, indicating "
                if analysis['rsi'] < 30:
                    nl_summary += "oversold conditions. "
                elif analysis['rsi'] > 70:
                    nl_summary += "overbought conditions. "
                else:
                    nl_summary += "neutral conditions. "
            
            if all(k in analysis for k in ['macd_line', 'macd_signal']):
                if analysis['macd_line'] > analysis['macd_signal']:
                    nl_summary += "The MACD indicator is bullish. "
                else:
                    nl_summary += "The MACD indicator is bearish. "
            
            nl_summary += f"The overall technical signal is {analysis.get('signal', 'hold')}."
            
            content += f"\nSummary: {nl_summary}\n"
            
            documents.append(Document(
                page_content=content,
                metadata={
                    "source": "technical_analysis",
                    "coin": coin,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "type": "technical_data",
                    "signal": analysis.get('signal', 'hold')
                }
            ))
        
        # Format news data
        for article in self.news_data:
            content = f"News: {article.get('title', 'No Title')}\n"
            content += f"Source: {article.get('source', {}).get('name', 'Unknown')}\n"
            content += f"Published: {article.get('publishedAt', 'Unknown')}\n"
            content += f"URL: {article.get('url', 'N/A')}\n\n"
            content += article.get('description', 'No description available') + "\n\n"
            content += article.get('content', 'No content available')
            
            # Extract related coins from title/description
            related_coins = self._extract_crypto_mentions(article.get('title', '') + ' ' + article.get('description', ''))
            
            # Add natural language summary for better RAG retrieval
            if related_coins:
                content += f"\nThis article discusses the following cryptocurrencies: {', '.join(related_coins)}.\n"
            
            documents.append(Document(
                page_content=content,
                metadata={
                    "source": "news",
                    "title": article.get('title', 'No Title'),
                    "published": article.get('publishedAt', 'Unknown'),
                    "timestamp": datetime.datetime.now().isoformat(),
                    "related_coins": related_coins,
                    "type": "news_article"
                }
            ))
        
        # Create a special document for date-based price lookups
        content = "Date-based price lookup reference:\n"
        content += "This document contains information about cryptocurrency prices on specific dates.\n"
        content += "You can use this to answer questions like 'What was the price of Bitcoin on 2025-05-06?'\n\n"
        
        # Add examples for common date formats
        content += "Common date formats supported:\n"
        content += "- YYYY-MM-DD (e.g., 2025-05-06)\n"
        content += "- MM/DD/YYYY (e.g., 05/06/2025)\n"
        content += "- Month DD, YYYY (e.g., May 6, 2025)\n\n"
        
        content += "When asked about a specific date, check the historical data for that date.\n"
        content += "If the exact date is not available, find the closest available date.\n"
        
        documents.append(Document(
            page_content=content,
            metadata={
                "source": "date_lookup_reference",
                "timestamp": datetime.datetime.now().isoformat(),
                "type": "reference"
            }
        ))
        
        return documents
    
    def verify_historical_data(self):
        """Verify historical data is properly loaded."""
        for coin, df in self.historical_data.items():
            if df is None or df.empty:
                logger.warning(f"No historical data for {coin}")
                continue
                
            # Ensure date column is datetime type
            if 'date' in df.columns:
                if not pd.api.types.is_datetime64_any_dtype(df['date']):
                    logger.info(f"Converting date column to datetime for {coin}")
                    df['date'] = pd.to_datetime(df['date'])
                    
            logger.info(f"Historical data for {coin}: {len(df)} records from {df['date'].min()} to {df['date'].max()}")
            
            # Check if price column exists
            if 'price' not in df.columns:
                logger.error(f"No price column in historical data for {coin}")
                if 'close' in df.columns:
                    logger.info(f"Adding price column from close for {coin}")
                    df['price'] = df['close']
                    
            # Update the dictionary
            self.historical_data[coin] = df

    
    def _extract_crypto_mentions(self, text: str) -> List[str]:
        """Extract cryptocurrency mentions from text."""
        mentioned_coins = []
        
        # Check for each coin and its aliases
        for standard_name, aliases in self.coin_aliases.items():
            all_forms = aliases + [standard_name]
            for form in all_forms:
                if re.search(r'\b' + re.escape(form) + r'\b', text.lower()):
                    mentioned_coins.append(standard_name)
                    break  # Found one form, no need to check others
        
        return list(set(mentioned_coins))  # Remove duplicates
    
    def answer_date_price_query(self, query: str) -> Tuple[bool, str]:
        """
        Special handler for date-based price queries.
        Returns (True, answer) if it's a date-price query that can be answered directly.
        Returns (False, "") if it's not a date-price query.
        """
        # Common date-price query patterns
 

        date_price_patterns = [
            # YYYY-MM-DD format (with support for multiple separators)
            r'(?:what|how much|price|cost).*?(?:bitcoin|btc).*?(?:on|at|for|during).*?(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})',
            r'(?:what|how much|price|cost).*?(?:on|at|for|during).*?(\d{4}[-/.]\d{1,2}[-/.]\d{1,2}).*?(?:bitcoin|btc)',
            r'(?:what|how much|price|trend|cost).*?(?:bitcoin|btc).*?(?:on|at|for|during|in).*?(\w+ \d{4})',
            r'(?:what|how much|price|trend|cost).*?(?:on|at|for|during|in).*?(\w+ \d{4}).*?(?:bitcoin|btc)',
            
            # MM-DD-YYYY format (with support for 2 or 4 digit years)
            r'(?:what|how much|price|cost).*?(?:bitcoin|btc).*?(?:on|at|for|during).*?(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})',
            r'(?:what|how much|price|cost).*?(?:on|at|for|during).*?(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}).*?(?:bitcoin|btc)',
            r'(?:price|value|cost).*?(?:bitcoin|btc).*?(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})',
            r'(?:price|value|cost).*?(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}).*?(?:bitcoin|btc)',
            
            # Month DD, YYYY format (e.g., "March 19, 2019")
            r'(?:what|how much|price|cost).*?(?:bitcoin|btc).*?(?:on|at|for|during).*?(\w+ \d{1,2}(?:st|nd|rd|th)?,? \d{2,4})',
            r'(?:what|how much|price|cost).*?(?:on|at|for|during).*?(\w+ \d{1,2}(?:st|nd|rd|th)?,? \d{2,4}).*?(?:bitcoin|btc)',
            
            # DD Month YYYY format (e.g., "18 March 2019") - The problematic format
            r'(?:what|how much|price|cost).*?(?:bitcoin|btc).*?(?:on|at|for|during).*?(\d{1,2}(?:st|nd|rd|th)? \w+ \d{2,4})',
            r'(?:what|how much|price|cost).*?(?:on|at|for|during).*?(\d{1,2}(?:st|nd|rd|th)? \w+ \d{2,4}).*?(?:bitcoin|btc)',
            
            # More flexible patterns for DD Month YYYY format
            r'(?:bitcoin|btc).*?(?:price|value|cost|worth).*?(\d{1,2}(?:st|nd|rd|th)? \w+ \d{2,4})',
            r'(\d{1,2}(?:st|nd|rd|th)? \w+ \d{2,4}).*?(?:bitcoin|btc).*?(?:price|value|cost|worth)',
            
            # Very permissive fallback patterns
            r'(?:bitcoin|btc).*?(\d{1,2}(?:st|nd|rd|th)? \w+ \d{2,4})',
            r'(\d{1,2}(?:st|nd|rd|th)? \w+ \d{2,4}).*?(?:bitcoin|btc)',
                    r'(?:what|how much|price|cost).*?(?:bitcoin|btc).*?(?:on|at|for|during).*?(yesterday|today|tomorrow)',
            r'(?:what|how much|price|cost).*?(?:on|at|for|during).*?(yesterday|today|tomorrow).*?(?:bitcoin|btc)',
            r'(?:price|value|cost).*?(?:bitcoin|btc).*?(yesterday|today|tomorrow)',
            r'(?:price|value|cost).*?(yesterday|today|tomorrow).*?(?:bitcoin|btc)',
            r'(?:what|how much).*?(?:bitcoin|btc).*?(yesterday|today|tomorrow)',
            r'(?:what|how much).*?(yesterday|today|tomorrow).*?(?:bitcoin|btc)',
            
            # Additional patterns for other relative date references
            r'(?:what|how much|price|cost).*?(?:bitcoin|btc).*?(?:on|at|for|during).*?(last week|last month|last year)',
            r'(?:what|how much|price|cost).*?(?:on|at|for|during).*?(last week|last month|last year).*?(?:bitcoin|btc)'
        ]
        
        # Try to match date and coin
        for pattern in date_price_patterns:
            date_match = re.search(pattern, query, re.IGNORECASE)
            if date_match:
                # Extract date
                date_str = date_match.group(1)
                if any(term in date_str.lower() for term in ['yesterday', 'today', 'tomorrow', 'last week', 'last month', 'last year']):
                    actual_date = self._convert_relative_date_to_actual(date_str)
                    if actual_date:
                        date_str = actual_date
                # Extract coin
                coin_pattern = r'(bitcoin|btc)'
                coin_match = re.search(coin_pattern, query, re.IGNORECASE)
                if coin_match:
                    coin = self.normalize_coin_name(coin_match.group(1))
                    
                    try:
                        # Try to parse the date
                        parsed_date = parser.parse(date_str, fuzzy=True)
                        formatted_date = parsed_date.strftime('%Y-%m-%d')
                        
                        # Get price for the date
                        price = self.get_price_for_date(coin, formatted_date)
                        
                        if price is not None:
                            response = f"The price of {coin} on {formatted_date} was ${price:.2f}."
                            
                            # Add context about price changes
                            if coin in self.price_data and 'usd' in self.price_data[coin]:
                                current_price = self.price_data[coin]['usd']
                                price_change = ((current_price / price) - 1) * 100
                                if price_change > 0:
                                    response += f" Since then, the price has increased by {price_change:.2f}% to the current price of ${current_price:.2f}."
                                else:
                                    response += f" Since then, the price has decreased by {abs(price_change):.2f}% to the current price of ${current_price:.2f}."
                                    
                            return True, response
                        else:
                            # Add information about what dates are available
                            if coin in self.date_price_lookup:
                                dates = list(self.date_price_lookup[coin].keys())
                                if dates:
                                    # Try nearby dates as fallback
                                    nearby_date = parser.parse(formatted_date)
                                    for offset in [1, 2, -1, -2]:
                                        test_date = nearby_date + datetime.timedelta(days=offset)
                                        test_date_str = test_date.strftime('%Y-%m-%d')
                                        if test_date_str in self.date_price_lookup[coin]:
                                            fallback_price = self.date_price_lookup[coin][test_date_str]
                                            return True, f"I don't have data specifically for {formatted_date}, but on {test_date_str}, the Bitcoin price was ${fallback_price:.2f}."
                            
                            return True, f"I couldn't find the price of {coin} on {formatted_date}. The data might not be available for that specific date."
                    except Exception as e:
                        logger.error(f"Error processing date price query: {str(e)}")
                        
        return False, ""

   

    def _convert_relative_date_to_actual(self, relative_date: str) -> str:
        """Convert relative date terms like 'yesterday' to actual dates."""
        today = datetime.datetime.now().date()
        
        if relative_date.lower() == 'yesterday':
            actual_date = today - datetime.timedelta(days=1)
        elif relative_date.lower() == 'today':
            actual_date = today
        elif relative_date.lower() == 'tomorrow':
            actual_date = today + datetime.timedelta(days=1)
        elif relative_date.lower() == 'last week':
            actual_date = today - datetime.timedelta(days=7)
        elif relative_date.lower() == 'last month':
            # Approximate last month as 30 days ago
            actual_date = today - datetime.timedelta(days=30)
        elif relative_date.lower() == 'last year':
            # Approximate last year as 365 days ago
            actual_date = today - datetime.timedelta(days=365)
        else:
            return None
        
        return actual_date.strftime('%Y-%m-%d')

    def process_prediction_query(self, query: str) -> Tuple[bool, int]:
        """
        Process a query to determine if it's asking for future price prediction.
        
        Args:
            query: User's question
            
        Returns:
            Tuple of (is_prediction_query, days_ahead)
        """
        import re
        
        # Check if this looks like a prediction query
        prediction_patterns = [
            r'(?:predict|forecast|projection|will be|going to be|future price)',
            r'(?:price|value|worth|cost).*?(?:in|after|next).*?(\d+)\s*(?:day|days|week|weeks|month|months)',
            r'(?:what will).*?(?:bitcoin|btc).*?(?:be worth|be priced|cost|price).*?(\d+)\s*(?:day|days|week|weeks|month|months)',
            r'(?:how much will).*?(?:bitcoin|btc).*?(?:be worth|cost|price).*?(\d+)\s*(?:day|days|week|weeks|month|months)',
            r'(?:price prediction|price forecast).*?(\d+)\s*(?:day|days|week|weeks|month|months)',
            r'(?:in|after|next)\s*(\d+)\s*(?:day|days|week|weeks|month|months).*?(?:bitcoin|btc).*?(?:price|value|worth|cost)'
        ]
        
        is_prediction_query = False
        days_ahead = 7  # Default
        
        for pattern in prediction_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                is_prediction_query = True
                # Try to extract number of days
                try:
                    # If the pattern contains a group for the number
                    if '(' in pattern and ')' in pattern:
                        unit_match = re.search(r'(\d+)\s*(day|days|week|weeks|month|months)', query, re.IGNORECASE)
                        if unit_match:
                            num = int(unit_match.group(1))
                            unit = unit_match.group(2).lower()
                            
                            # Convert to days
                            if 'week' in unit:
                                days_ahead = num * 7
                            elif 'month' in unit:
                                days_ahead = num * 30
                            else:
                                days_ahead = num
                except Exception as e:
                    # If extraction fails, use default
                    logger.warning(f"Failed to extract time period from prediction query: {e}")
                    pass  # Keep the default value
        
        # Ensure days is within a reasonable range
        days_ahead = min(max(days_ahead, 1), 30)  # Between 1 and 30 days (matches self.prediction_days)
        
        return (is_prediction_query, days_ahead)
   

    def process_query_for_nlp_enhancement(self, query: str) -> Dict[str, Any]:
        """Process query to extract dates, coins, and timeframes for enhanced NLP understanding."""
        result = {
            "is_date_query": False,
            "is_price_query": False,
            "is_comparison_query": False,
            "is_trend_query": False,
            "coins": [],
            "dates": [],
            "timeframes": []
        }
        
        # Check if query is about price
        if re.search(r'(price|cost|worth|value|how much)', query, re.IGNORECASE):
            result["is_price_query"] = True
        
        # Check if query is about comparisons
        if re.search(r'(compare|comparison|versus|vs|difference|better|worse|higher|lower|more expensive|cheaper)', query, re.IGNORECASE):
            result["is_comparison_query"] = True
        
         # Check if query is about trends
        if re.search(r'(trend|movement|performance|growth|decline|increase|decrease|uptrend|downtrend|bullish|bearish|rise|fall)', query, re.IGNORECASE):
            result["is_trend_query"] = True
        
        
        # Extract coins mentioned
        for standard_name, aliases in self.coin_aliases.items():
            all_forms = aliases + [standard_name]
            for form in all_forms:
                if re.search(r'\b' + re.escape(form) + r'\b', query.lower()):
                    result["coins"].append(standard_name)
                    break
        
        # Extract dates
        date_patterns = [
            r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',  # YYYY-MM-DD or YYYY/MM/DD
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})',  # MM-DD-YYYY or MM/DD/YYYY
            r'(\w+ \d{1,2},? \d{4})',  # Month DD, YYYY
            r'(\d{1,2} \w+ \d{4})',  # DD Month YYYY
            r'(\w+ \d{4})',  # Month YYYY
            r'(\d{4})'  # Just a year
        ]
        
        for pattern in date_patterns:
            dates = re.findall(pattern, query)
            if dates:
                result["is_date_query"] = True
                for date_str in dates:
                    try:
                        parsed_date = parser.parse(date_str, fuzzy=True)
                        result["dates"].append(parsed_date.strftime('%Y-%m-%d'))
                    except:
                        pass
        
        # Extract timeframes
        timeframe_patterns = {
            "day": r'\b(day|daily|24\s*hours?)\b',
            "week": r'\b(week|weekly|7\s*days?)\b',
            "month": r'\b(month|monthly|30\s*days?)\b',
            "quarter": r'\b(quarter|quarterly|3\s*months?|90\s*days?)\b',
            "year": r'\b(year|yearly|annual|12\s*months?|365\s*days?)\b'
        }
        
        for timeframe, pattern in timeframe_patterns.items():
            if re.search(pattern, query, re.IGNORECASE):
                result["timeframes"].append(timeframe)
        
        return result
    def verify_historical_data(self):
        """Verify historical data is properly loaded."""
        for coin, df in self.historical_data.items():
            if df is None or df.empty:
                logger.warning(f"No historical data for {coin}")
                continue
                
            logger.info(f"Historical data for {coin}: {len(df)} records from {df['date'].min()} to {df['date'].max()}")
            logger.info(f"Columns available: {df.columns.tolist()}")
            
            # Check if price column exists
            if 'price' not in df.columns:
                logger.error(f"No price column in historical data for {coin}")
                if 'close' in df.columns:
                    logger.info(f"Adding price column from close for {coin}")
                    df['price'] = df['close']
                    
            # Update the dictionary
            self.historical_data[coin] = df

    
    def get_coin_comparison(self, coins: List[str], timeframe: str = "month") -> str:
        """Generate a comparison between two or more coins over a specified timeframe."""
        if len(coins) < 2 or not all(coin in self.historical_data for coin in coins):
            return "Unable to compare the requested coins. Some data might be missing."
        
        periods = {
            "day": 1,
            "week": 7,
            "month": 30,
            "quarter": 90,
            "year": 365
        }
        
        days = periods.get(timeframe, 30)  # Default to month
        
        comparison = f"Comparison of {', '.join(coins)} over the past {timeframe}:\n\n"
        
        # Collect performance data
        performances = {}
        for coin in coins:
            df = self.historical_data.get(coin)
            if df is None or df.empty or len(df) < days:
                performances[coin] = {"error": f"Insufficient historical data for {coin}"}
                continue
                
            last_period = df.iloc[-days:]
            start_price = last_period['price'].iloc[0]
            end_price = last_period['price'].iloc[-1]
            period_change = ((end_price / start_price) - 1) * 100
            high = last_period['price'].max()
            low = last_period['price'].min()
            volatility = last_period['price'].pct_change().std() * 100 if len(last_period) > 1 else 0
            
            performances[coin] = {
                "start_price": start_price,
                "current_price": end_price,
                "period_change": period_change,
                "high": high,
                "low": low,
                "volatility": volatility
            }
            
        # Create comparison table
        comparison += "Performance Metrics:\n"
        for coin, data in performances.items():
            if "error" in data:
                comparison += f"{coin}: {data['error']}\n"
                continue
                
            comparison += f"{coin}:\n"
            comparison += f"  Starting Price: ${data['start_price']:.2f}\n"
            comparison += f"  Current Price: ${data['current_price']:.2f}\n"
            comparison += f"  {timeframe.capitalize()} Change: {data['period_change']:.2f}%\n"
            comparison += f"  {timeframe.capitalize()} High: ${data['high']:.2f}\n"
            comparison += f"  {timeframe.capitalize()} Low: ${data['low']:.2f}\n"
            comparison += f"  Volatility: {data['volatility']:.2f}%\n\n"
        
        # Determine best performer
        valid_coins = [coin for coin in coins if coin in performances and "error" not in performances[coin]]
        if valid_coins:
            best_performer = max(valid_coins, key=lambda x: performances[x]["period_change"])
            worst_performer = min(valid_coins, key=lambda x: performances[x]["period_change"])
            
            comparison += f"Best Performer: {best_performer} with {performances[best_performer]['period_change']:.2f}% change\n"
            comparison += f"Worst Performer: {worst_performer} with {performances[worst_performer]['period_change']:.2f}% change\n\n"
            
            # Add analytical insight
            comparison += "Analysis:\n"
            if performances[best_performer]["period_change"] > 0:
                comparison += f"The {timeframe} has been generally positive for {best_performer}, outperforming other coins in this comparison."
            else:
                comparison += f"Despite being the best performer, {best_performer} still showed a negative return of {performances[best_performer]['period_change']:.2f}% in this {timeframe}."
            
            # Add volatility insight
            most_volatile = max(valid_coins, key=lambda x: performances[x]["volatility"])
            least_volatile = min(valid_coins, key=lambda x: performances[x]["volatility"])
            
            comparison += f"\n\n{most_volatile} showed the highest volatility at {performances[most_volatile]['volatility']:.2f}%, "
            comparison += f"while {least_volatile} was the most stable with {performances[least_volatile]['volatility']:.2f}% volatility."
        
        return comparison
    
    def update_sentiment_analysis(self):
        """Update sentiment analysis for news data."""
        try:
            if not self.news_data:
                logger.warning("No news data available for sentiment analysis")
                return False

            logger.info(f"Performing sentiment analysis on {len(self.news_data)} news articles")
            
            # Initialize sentiment analyzer if not already done
            if not hasattr(self, 'sentiment_analyzer') or not self.sentiment_analyzer:
                from sentiment_analyzer import CryptoSentimentAnalyzer
                self.sentiment_analyzer = CryptoSentimentAnalyzer()
                
            self.sentiment_results = self.sentiment_analyzer.analyze_news_batch(self.news_data)
            logger.info(f"Sentiment analysis complete: {self.sentiment_results['overall_sentiment']}")
            return True
        except Exception as e:
            logger.error(f"Error updating sentiment analysis: {str(e)}")
            # Set a basic sentiment structure even if there's an error
            self.sentiment_results = {"overall_sentiment": "neutral", "score": 0, "articles_analyzed": 0}
            return False

    def update_technical_analysis(self, coins=["bitcoin"]):
        """Update technical analysis for historical data."""
        try:
            self.technical_analysis = {}
            
            for coin in coins:
                if coin not in self.historical_data or self.historical_data[coin] is None:
                    logger.warning(f"No historical data available for {coin}")
                    continue
                    
                df = self.historical_data[coin]
                if df is None or df.empty or 'price' not in df.columns:
                    logger.warning(f"Invalid historical data for {coin}")
                    continue
                    
                logger.info(f"Performing technical analysis for {coin}")
                
                # Calculate indicators
                df_with_indicators = df.copy()
                df_with_indicators = self.technical_indicators.calculate_rsi(df_with_indicators)
                df_with_indicators = self.technical_indicators.calculate_macd(df_with_indicators)
                df_with_indicators = self.technical_indicators.calculate_bollinger_bands(df_with_indicators)
                
                # Generate signals
                df_with_indicators = self.technical_indicators.generate_signals(df_with_indicators)
                
                # Store the enhanced dataframe
                self.historical_data[coin] = df_with_indicators
                
                # Generate analysis summary
                analysis = self.technical_indicators.analyze_historical_data(df_with_indicators)
                self.technical_analysis[coin] = analysis
                
                logger.info(f"Technical analysis complete for {coin}: {analysis['signal']}")
            
            return True
        except Exception as e:
            logger.error(f"Error updating technical analysis: {str(e)}")
            return False

    def get_sentiment_summary(self) -> str:
        """Get a summary of current market sentiment."""
        if not hasattr(self, 'sentiment_results') or not self.sentiment_results:
            # Attempt to update sentiment data when missing
            try:
                normalized_coins = [self.normalize_coin_name(coin) for coin in ["bitcoin"]]
                news_data = self.news_api.fetch_crypto_news(normalized_coins)
                if news_data:
                    self.news_data = news_data
                    self.update_sentiment_analysis()
                    logger.info(f"Sentiment data updated on demand: {len(news_data)} articles analyzed")
                else:
                    return "No sentiment data available. Unable to fetch news articles."
            except Exception as e:
                logger.error(f"Failed to update sentiment data on demand: {e}")
                return "No sentiment data available. Please update the data first."
        """Get a summary of current market sentiment."""
        if not self.sentiment_results:
            return "No sentiment data available. Please update the data first."
            
        summary = f"Market Sentiment Analysis (as of {self.last_update.strftime('%Y-%m-%d %H:%M:%S') if self.last_update else 'unknown'}):\n\n"
        
        # Overall sentiment
        summary += f"Overall Market Sentiment: {self.sentiment_results['overall_sentiment'].capitalize()}\n"
        summary += f"Sentiment Score: {self.sentiment_results['score']:.2f} (Range: -1 to 1)\n"
        summary += f"Articles Analyzed: {self.sentiment_results['articles_analyzed']}\n\n"
        
        # Get sentiment trend if available
        trend_data = self.sentiment_analyzer.get_sentiment_trend(days=7)
        if trend_data and trend_data['data']:
            summary += f"7-Day Sentiment Trend: {trend_data['trend'].capitalize()}\n"
            summary += f"Average 7-Day Score: {trend_data['avg_score']:.2f}\n\n"
        
        # Most positive and negative articles
        if 'article_sentiments' in self.sentiment_results:
            articles = sorted(self.sentiment_results['article_sentiments'], 
                            key=lambda x: x['compound_score'], reverse=True)
            
            if articles:
                # Most positive article
                summary += "Most Positive Article:\n"
                summary += f"Title: {articles[0]['title']}\n"
                summary += f"Source: {articles[0]['source']}\n"
                summary += f"Sentiment: {articles[0]['sentiment'].capitalize()} ({articles[0]['compound_score']:.2f})\n\n"
                
                # Most negative article
                if len(articles) > 1:
                    most_negative = articles[-1]
                    summary += "Most Negative Article:\n"
                    summary += f"Title: {most_negative['title']}\n"
                    summary += f"Source: {most_negative['source']}\n"
                    summary += f"Sentiment: {most_negative['sentiment'].capitalize()} ({most_negative['compound_score']:.2f})\n"
        
        return summary

    def get_technical_analysis_summary(self, coin: str) -> str:
        """Get a summary of technical analysis for a specific coin."""
        if not self.technical_analysis or coin not in self.technical_analysis:
            return f"No technical analysis available for {coin}. Please update the data first."
            
        analysis = self.technical_analysis[coin]
        
        summary = f"Technical Analysis for {coin.capitalize()} (as of {analysis.get('analysis_date', 'unknown')}):\n\n"
        
        # Current price and indicators
        summary += f"Current Price: ${analysis.get('price', 'N/A'):.2f}\n\n"
        
        # RSI analysis
        if 'rsi' in analysis:
            rsi_value = analysis['rsi']
            summary += f"RSI: {rsi_value:.2f}\n"
            if rsi_value < 30:
                summary += "RSI Indication: Oversold (Potential buying opportunity)\n"
            elif rsi_value > 70:
                summary += "RSI Indication: Overbought (Potential selling opportunity)\n"
            else:
                summary += "RSI Indication: Neutral\n"
        
        # MACD analysis
        if all(k in analysis for k in ['macd_line', 'macd_signal', 'macd_histogram']):
            summary += f"\nMACD Line: {analysis['macd_line']:.2f}\n"
            summary += f"MACD Signal: {analysis['macd_signal']:.2f}\n"
            summary += f"MACD Histogram: {analysis['macd_histogram']:.2f}\n"
            
            if analysis['macd_line'] > analysis['macd_signal']:
                summary += "MACD Indication: Bullish (MACD above Signal Line)\n"
            else:
                summary += "MACD Indication: Bearish (MACD below Signal Line)\n"
                
            if analysis['macd_histogram'] > 0 and analysis['macd_histogram'] > analysis.get('macd_histogram_prev', 0):
                summary += "MACD Histogram: Increasing positive (Strong bullish momentum)\n"
            elif analysis['macd_histogram'] > 0:
                summary += "MACD Histogram: Positive (Bullish momentum)\n"
            elif analysis['macd_histogram'] < 0 and analysis['macd_histogram'] < analysis.get('macd_histogram_prev', 0):
                summary += "MACD Histogram: Increasing negative (Strong bearish momentum)\n"
            else:
                summary += "MACD Histogram: Negative (Bearish momentum)\n"
        
        # Bollinger Bands analysis
        if all(k in analysis for k in ['bollinger_upper', 'bollinger_middle', 'bollinger_lower']):
            summary += f"\nBollinger Middle Band: ${analysis['bollinger_middle']:.2f}\n"
            summary += f"Bollinger Upper Band: ${analysis['bollinger_upper']:.2f}\n"
            summary += f"Bollinger Lower Band: ${analysis['bollinger_lower']:.2f}\n"
            
            price = analysis.get('price', 0)
            if price > analysis['bollinger_upper']:
                summary += "Bollinger Bands: Price above upper band (Potential overbought condition)\n"
            elif price < analysis['bollinger_lower']:
                summary += "Bollinger Bands: Price below lower band (Potential oversold condition)\n"
            else:
                bandwidth = (analysis['bollinger_upper'] - analysis['bollinger_lower']) / analysis['bollinger_middle']
                if bandwidth < 0.1:
                    summary += "Bollinger Bands: Bands are squeezing (Potential breakout ahead)\n"
                else:
                    summary += "Bollinger Bands: Price within bands (Normal volatility)\n"
        
        # Overall analysis
        summary += f"\nMarket Condition: {analysis.get('market_condition', 'Unknown').capitalize()}\n"
        summary += f"Trend: {analysis.get('trend', 'Unknown').capitalize()}\n"
        summary += f"Volatility: {analysis.get('volatility', 'Unknown').replace('_', ' ').capitalize()}\n"
        summary += f"Overall Signal: {analysis.get('signal', 'Hold').replace('_', ' ').capitalize()}\n"
        
        return summary