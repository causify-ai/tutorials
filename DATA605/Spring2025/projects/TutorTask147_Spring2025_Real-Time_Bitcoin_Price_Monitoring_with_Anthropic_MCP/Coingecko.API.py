# coingecko.API.py
"""
Real‑Time Bitcoin data retrieval using the CoinGecko API.

1. Include citations here for code and research:
   - CoinGecko API Documentation v3: https://www.coingecko.com/api/documentations/v3
2. Run the linter on this script before committing changes.
   - Use tools like flake8 or pylint to enforce coding style.
3. Reference detailed system documentation:
   - See Coingecko.API.md for full API usage and parameter details.

Script naming convention: <project>.API.py (here: coingecko.API.py).
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import requests

_LOG = logging.getLogger(__name__)


def get_bitcoin_price(vs_currency: str = "usd") -> float:
    """
    Fetch the current Bitcoin price in the specified currency.

    :param vs_currency: The target currency (e.g., 'usd').
    :return: The current price of Bitcoin.
    """
    # Build request URL and parameters.
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": vs_currency}
    # Send HTTP GET request.
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    # Extract and return price.
    price = data["bitcoin"][vs_currency]
    _LOG.debug("Fetched BTC price: %s %s", price, vs_currency)
    return price


def get_coin_ohlc(
    coin_id: str = "bitcoin",
    vs_currency: str = "usd",
    days: int = 7
) -> List[List[Any]]:
    """
    Retrieve OHLC data for a coin over the last N days.

    :param coin_id: The CoinGecko coin identifier.
    :param vs_currency: The currency to denominate values.
    :param days: Number of days of historical data.
    :return: A list of [timestamp, open, high, low, close].
    """
    # Build request URL and parameters.
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
    params = {"vs_currency": vs_currency, "days": days}
    # Send HTTP GET request.
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    _LOG.debug("Fetched %d OHLC points for %s", len(data), coin_id)
    return data


def get_historical_data(
    coin_id: str = "bitcoin",
    date_str: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch historical snapshot for a coin on a specific date.

    :param coin_id: The CoinGecko coin identifier.
    :param date_str: Target date in DD-MM-YYYY format (defaults to today).
    :return: JSON dictionary with market_data and metadata.
    """
    # Use today's date if none provided.
    if date_str is None:
        date_str = datetime.utcnow().strftime("%d-%m-%Y")
    # Build request URL and parameters.
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/history"
    params = {"date": date_str}
    # Send HTTP GET request.
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    _LOG.debug("Fetched historical data for %s on %s", coin_id, date_str)
    return data


def get_market_chart(
    coin_id: str = "bitcoin",
    vs_currency: str = "usd",
    days: int = 30
) -> Dict[str, List[Any]]:
    """
    Retrieve market chart data (prices, caps, volumes) for the past N days.

    :param coin_id: The CoinGecko coin identifier.
    :param vs_currency: The currency to denominate values.
    :param days: Number of days of historical data.
    :return: Dictionary with 'prices', 'market_caps', and 'total_volumes'.
    """
    # Build request URL and parameters.
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": vs_currency, "days": days}
    # Send HTTP GET request.
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    _LOG.debug("Fetched market chart data for %s: %d price points", coin_id, len(data["prices"]))
    return data


def main() -> None:
    """
    Demonstrate usage of CoinGecko API functions.
    """
    # Configure logging format.
    logging.basicConfig(level=logging.INFO)
    _LOG.info("Starting CoinGecko API client demonstration.")
    price = get_bitcoin_price()
    _LOG.info("Current BTC price: $%0.2f USD", price)
    ohlc = get_coin_ohlc(days=7)
    _LOG.info("Retrieved %d OHLC entries.", len(ohlc))
    hist = get_historical_data(date_str="01-01-2025")
    _LOG.info(
        "BTC price on 01-01-2025: $%0.2f USD",
        hist.get("market_data", {}).get("current_price", {}).get("usd", float("nan"))
    )
    chart = get_market_chart(days=30)
    _LOG.info("Retrieved %d price points for market chart.", len(chart["prices"]))
    _LOG.info("CoinGecko API client demonstration complete.")


if __name__ == "__main__":
    main()