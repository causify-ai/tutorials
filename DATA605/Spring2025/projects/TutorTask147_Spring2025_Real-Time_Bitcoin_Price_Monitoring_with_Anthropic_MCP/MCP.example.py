"""
A brief overview of what the script does in one line.

1. Make sure to include the citations here (code and research)
2. Make sure to run the linter on the script before committing changes.
    - Many changes would be pointed out by the linter to maintain consistency
      with coding style.
3. Provide here the reference to the documentation that explains the system in
   detail. (e.g., pycaret.API.md)

This script is how you use (customize) the API in the project. The
naming should be as follows:
 - if the project is on `pycaret`, then it is `pycaret.example.py`

 Follow the reference on coding style guide to write clean and readable code.
- https://github.com/causify-ai/helpers/blob/master/docs/coding/all.coding_style.how_to_guide.md
"""

# Same as tutorial_template/template.API.py
from typing import Any
from datetime import datetime
import requests
import pandas as pd
import statsmodels.api as sm
import plotly.express as px
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("bitcoin_monitor")
BASE_URL = "https://api.coingecko.com/api/v3"
THRESHOLD = 500.0  # USD price-change threshold
_last_price: float | None = None

@mcp.resource("crypto://price")
async def get_price() -> float:
   """Return the latest BTC price in USD."""
   url = f"{BASE_URL}/simple/price"
   params = {"ids": "bitcoin", "vs_currencies": "usd"}
   resp = requests.get(url, params=params)
   resp.raise_for_status()
   return resp.json()["bitcoin"]["usd"]

@mcp.tool()
async def get_ohlc(days: int = 7) -> list[Any]:
   """
   Return a list of [timestamp, open, high, low, close] for the past `days` days.
   """
   url = f"{BASE_URL}/coins/bitcoin/ohlc"
   params = {"vs_currency": "usd", "days": days}
   resp = requests.get(url, params=params)
   resp.raise_for_status()
   return resp.json()

@mcp.tool()
async def get_history(date: str) -> dict[str, Any]:
   """Return the BTC market snapshot on the given date."""
   url = f"{BASE_URL}/coins/bitcoin/history"
   params = {"date": date}
   resp = requests.get(url, params=params)
   resp.raise_for_status()
   return resp.json()

@mcp.tool("alert://price_change")
async def check_price_change(threshold: float = THRESHOLD) -> str:
   """
   Compare current price to last fetched price. If change > threshold, return an alert.
   """
   global _last_price
   price = get_price()
   if _last_price is None:
      _last_price = price
      return "Initialized last_price"
   delta = abs(price - _last_price)
   _last_price = price
   return (
      f"Alert: price moved ${delta:.2f}"
      if delta >= threshold
      else "No significant change"
   )

@mcp.tool()
async def detect_trend(days: int = 30) -> str:
   """
   Fit an ARIMA model to daily-averaged price data over the past `days` days
   and return the latest predicted value.
   """
   # Get market-chart data
   url = f"{BASE_URL}/coins/bitcoin/market_chart"
   params = {"vs_currency": "usd", "days": days}
   data = requests.get(url, params=params).json()["prices"]
   # Build DataFrame
   df = pd.DataFrame(data, columns=["timestamp", "price"])
   df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")
   df.set_index("datetime", inplace=True)
   daily = df["price"].resample("D").mean()
   # Fit SARIMAX(1,1,1)
   model = sm.tsa.SARIMAX(daily, order=(1,1,1)).fit(disp=False)
   pred = model.get_prediction(start=daily.index[-1], end=daily.index[-1])
   return f"Trend forecast for {daily.index[-1].date()}: {pred.predicted_mean.iloc[0]:.2f}"

@mcp.tool()
async def plot_price(days: int = 7) -> str:
   """
   Create a Plotly line chart of BTC prices over the last `days` days.
   Returns the path to an HTML file with the chart.
   """
   # Fetch data
   url = f"{BASE_URL}/coins/bitcoin/market_chart"
   params = {"vs_currency": "usd", "days": days}
   data = requests.get(url, params=params).json()["prices"]
   df = pd.DataFrame(data, columns=["timestamp", "price"])
   df["datetime"] = pd.to_datetime(df["timestamp"], unit="ms")
   # Plot
   fig = px.line(df, x="datetime", y="price", title="Bitcoin Price (USD)")  
   out = "bitcoin_price.html"
   fig.write_html(out)
   return out

if __name__ == "__main__":
   print("MCP server activate!")
   mcp.run(transport="stdio")
