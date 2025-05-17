"""
Bitcoin Price Monitoring System using FastMCP.

1. Citations:
   - CoinGecko API: https://www.coingecko.com/api/documentation
   - statsmodels SARIMAX: https://www.statsmodels.org/stable/generated/statsmodels.tsa.statespace.sarimax.SARIMAX.html
   - FastMCP Framework:       

2. For detailed system documentation, see:
   - MCP.exapmle.API.md

This script implements a Bitcoin monitoring system using FastMCP framework.
It provides tools for price checking, trend analysis, and alerts when significant
price changes occur.
"""

from datetime import datetime
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple, Union
import asyncio
import logging

import aiohttp
import pandas as pd
import plotly.express as px
import statsmodels.api as sm
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("bitcoin_monitor")

# Initialize MCP server
mcp = FastMCP("bitcoin_monitor")

# Constants
BASE_URL = "https://api.coingecko.com/api/v3"
THRESHOLD = 500.0  # USD price-change threshold
RETRY_ATTEMPTS = 3
RETRY_DELAY = 2  # seconds


class PriceState:
    """Class to manage price state instead of using globals."""
    
    def __init__(self):
        self._last_price: Optional[float] = None
    
    @property
    def last_price(self) -> Optional[float]:
        return self._last_price
    
    @last_price.setter
    def last_price(self, value: float) -> None:
        self._last_price = value


# Initialize state
price_state = PriceState()


async def make_api_request(url: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Make an API request with retry logic.
    
    Args:
        url: API endpoint URL
        params: Query parameters
        
    Returns:
        JSON response as dictionary
        
    Raises:
        aiohttp.ClientError: If request fails after all retries
    """
    for attempt in range(RETRY_ATTEMPTS):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 429:  # Rate limited
                        wait_time = int(response.headers.get("Retry-After", RETRY_DELAY))
                        logger.warning(f"Rate limited. Waiting {wait_time} seconds.")
                        await asyncio.sleep(wait_time)
                        continue
                        
                    response.raise_for_status()
                    return await response.json()
                    
        except aiohttp.ClientError as e:
            logger.error(f"Request failed (attempt {attempt+1}/{RETRY_ATTEMPTS}): {str(e)}")
            if attempt < RETRY_ATTEMPTS - 1:
                await asyncio.sleep(RETRY_DELAY * (attempt + 1))  # Exponential backoff
            else:
                raise
    
    raise RuntimeError("Failed to make API request after multiple attempts")


def validate_days(days: int) -> int:
    """Validate days parameter is within acceptable range."""
    if not isinstance(days, int):
        raise TypeError("days must be an integer")
    if days < 1 or days > 365:
        raise ValueError("days must be between 1 and 365")
    return days


def validate_date(date_str: str) -> str:
    """Validate date string is in the format dd-mm-yyyy."""
    try:
        datetime.strptime(date_str, "%d-%m-%Y")
        return date_str
    except ValueError:
        raise ValueError("date must be in format dd-mm-yyyy")


@mcp.resource("crypto://price")
async def get_price() -> float:
    """
    Return the latest BTC price in USD.
    
    Returns:
        Current Bitcoin price in USD
        
    Raises:
        RuntimeError: If unable to fetch price after retries
    """
    url = f"{BASE_URL}/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": "usd"}
    
    try:
        data = await make_api_request(url, params)
        price = data["bitcoin"]["usd"]
        logger.info(f"Current BTC price: ${price}")
        return price
    except KeyError:
        logger.error("Unexpected API response format")
        raise RuntimeError("Failed to parse Bitcoin price from API response")


@mcp.tool("get_ohlc")
async def get_ohlc(days: int = 7) -> List[List[Union[int, float]]]:
    """
    Return OHLC data for Bitcoin over specified period.
    
    Args:
        days: Number of days of historical data (1-365)
        
    Returns:
        List of [timestamp, open, high, low, close] data points
        
    Raises:
        ValueError: If days parameter is invalid
    """
    days = validate_days(days)
    
    url = f"{BASE_URL}/coins/bitcoin/ohlc"
    params = {"vs_currency": "usd", "days": days}
    
    data = await make_api_request(url, params)
    logger.info(f"Retrieved {len(data)} OHLC data points")
    return data


@mcp.tool("get_history")
async def get_history(date: str) -> Dict[str, Any]:
    """
    Return the BTC market snapshot on the given date.
    
    Args:
        date: Date in format dd-mm-yyyy
        
    Returns:
        Dictionary with Bitcoin market data for specified date
        
    Raises:
        ValueError: If date format is invalid
    """
    validated_date = validate_date(date)
    
    url = f"{BASE_URL}/coins/bitcoin/history"
    params = {"date": validated_date}
    
    data = await make_api_request(url, params)
    logger.info(f"Retrieved historical data for {validated_date}")
    return data


@mcp.tool("alert_price_change")
async def check_price_change(threshold: float = THRESHOLD) -> str:
    """
    Compare current price to last fetched price and return alert if change exceeds threshold.
    
    Args:
        threshold: USD amount that triggers an alert (default: 500.0)
        
    Returns:
        Alert message or status message
    """
    if threshold <= 0:
        raise ValueError("Threshold must be positive")
        
    try:
        current_price = await get_price()
        
        if price_state.last_price is None:
            price_state.last_price = current_price
            return "Initialized price tracking"
            
        delta = abs(current_price - price_state.last_price)
        price_state.last_price = current_price
        
        if delta >= threshold:
            logger.warning(f"Price alert triggered: ${delta:.2f} change")
            return f"ALERT: Bitcoin price moved ${delta:.2f}"
        else:
            return f"No significant change (${delta:.2f})"
            
    except Exception as e:
        logger.error(f"Error checking price change: {str(e)}")
        return f"Error monitoring price: {str(e)}"


@lru_cache(maxsize=32)
async def _fetch_market_chart(days: int) -> pd.DataFrame:
    """
    Fetch and process market chart data.
    
    Args:
        days: Number of days of historical data
        
    Returns:
        DataFrame with processed price data
    """
    url = f"{BASE_URL}/coins/bitcoin/market_chart"
    params = {"vs_currency": "usd", "days": days}
    
    data = await make_api_request(url, params)
    
    df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
    df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("datetime", inplace=True)
    
    return df


@mcp.tool("detect_trend")
async def detect_trend(days: int = 30) -> Dict[str, Any]:
    """
    Fit an ARIMA model to price data and return trend analysis.
    
    Args:
        days: Number of days of historical data for trend analysis (1-365)
        
    Returns:
        Dictionary with trend analysis results
    """
    days = validate_days(days)
    
    try:
        df = await _fetch_market_chart(days)
        daily = df["price"].resample("D").mean()
        
        # Fit SARIMAX model
        model = sm.tsa.SARIMAX(
            daily, 
            order=(1, 1, 1),
            enforce_stationarity=False
        ).fit(disp=False)
        
        # Get prediction for tomorrow
        pred = model.get_forecast(steps=1)
        pred_mean = pred.predicted_mean.iloc[0]
        pred_ci = pred.conf_int()
        lower_bound = pred_ci.iloc[0, 0]
        upper_bound = pred_ci.iloc[0, 1]
        
        # Clear cache on error as well
        _fetch_market_chart.cache_clear()
        
        return {
            "date": daily.index[-1].date().isoformat(),
            "last_price": daily.iloc[-1],
            "predicted_price": pred_mean,
            "confidence_interval": (lower_bound, upper_bound),
            "trend": "up" if pred_mean > daily.iloc[-1] else "down",
            "message": f"Trend forecast for tomorrow: ${pred_mean:.2f} (95% CI: ${lower_bound:.2f} - ${upper_bound:.2f})"
        }
        
    except Exception as e:
        logger.error(f"Error detecting trend: {str(e)}")
        # Clear cache on error as well
        _fetch_market_chart.cache_clear()
        raise


@mcp.tool("plot_price")
async def plot_price(days: int = 7) -> str:
    """
    Create a Plotly line chart of BTC prices.
    
    Args:
        days: Number of days of historical data to plot (1-365)
        
    Returns:
        Path to saved HTML file with the interactive chart
    """
    days = validate_days(days)
    
    try:
        df = await _fetch_market_chart(days)
        
        # Reset index to make datetime a column for Plotly
        plot_df = df.reset_index()
        
        # Create plot
        fig = px.line(
            plot_df, 
            x="datetime", 
            y="price",
            title=f"Bitcoin Price (USD) - Last {days} Days",
            labels={"datetime": "Date", "price": "Price (USD)"}
        )
        
        fig.update_layout(
            template="plotly_white",
            hovermode="x unified",
            hoverlabel=dict(bgcolor="white"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02)
        )
        
        # Add moving averages
        if days >= 7:
            plot_df["MA7"] = plot_df["price"].rolling(window=7*24).mean()  # 7-day MA
            fig.add_scatter(x=plot_df["datetime"], y=plot_df["MA7"], 
                           name="7-Day MA", line=dict(width=1))
        
        if days >= 30:
            plot_df["MA30"] = plot_df["price"].rolling(window=30*24).mean()  # 30-day MA
            fig.add_scatter(x=plot_df["datetime"], y=plot_df["MA30"], 
                           name="30-Day MA", line=dict(width=1))
        
        # Save to file with timestamp to avoid overwrites
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bitcoin_price_{timestamp}.html"
        fig.write_html(filename)
        
        logger.info(f"Price chart saved to {filename}")
        # Clear cache on error as well
        _fetch_market_chart.cache_clear()
        return filename
        
    except Exception as e:
        logger.error(f"Error creating plot: {str(e)}")
        # Clear cache on error as well
        _fetch_market_chart.cache_clear()
        raise


@mcp.tool("get_summary")
async def get_summary() -> Dict[str, Any]:
    """
    Generate a comprehensive summary of Bitcoin's current status.
    
    Returns:
        Dictionary with summary information
    """
    try:
        price = await get_price()
        trend_data = await detect_trend(days=30)
        
        # Get 24h price change
        day_data = await _fetch_market_chart(days=2)
        day_prices = day_data["price"].resample("D").mean()
        price_24h_ago = day_prices.iloc[-2] if len(day_prices) >= 2 else None
        
        # Clear cache on error as well
        _fetch_market_chart.cache_clear()

        change_24h = None
        change_24h_percent = None
        
        if price_24h_ago is not None:
            change_24h = price - price_24h_ago
            change_24h_percent = (change_24h / price_24h_ago) * 100
        
        return {
            "timestamp": datetime.now().isoformat(),
            "current_price": price,
            "24h_change": change_24h,
            "24h_change_percent": change_24h_percent,
            "trend_forecast": trend_data["predicted_price"],
            "trend_direction": trend_data["trend"],
            "message": f"Bitcoin is currently ${price:,.2f} ({change_24h_percent:+.2f}% in 24h). " 
                     f"Forecast: {trend_data['trend'].upper()} trend to ${trend_data['predicted_price']:,.2f}."
        }
        
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        # Clear cache on error as well
        _fetch_market_chart.cache_clear()
        raise


if __name__ == "__main__":
    logger.info("Bitcoin Monitor MCP server starting...")
    mcp.run(transport="stdio")