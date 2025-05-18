"""
bitcoin_petl_utils.py

Utility functions to fetch and process Bitcoin price data via Petl.
Keeps the tutorials notebook clean by handling all API & ETL logic here.
"""
import time
import requests
import petl as etl

# API endpoint for CoinGecko simple price
CG_URL = (
    "https://api.coingecko.com/api/v3/simple/price"
    "?ids=bitcoin"
    "&vs_currencies=usd"
    "&include_last_updated_at=true"
)
def fetch_btc_price_table() -> etl.Table:
    """
    Hit CoinGecko and grab the latest BTC price in USD.
    Returns a one-row Petl table with:
      - timestamp: UNIX seconds
      - price_usd: float
    """
    resp = requests.get(CG_URL)
    resp.raise_for_status()
    info = resp.json().get("bitcoin", {})
    row = {
        "timestamp": info.get("last_updated_at"),
        "price_usd": info.get("usd")
    }
    # Here we wrap it up in a Petl table for easy downstream ETL
    return etl.fromdicts([row])

def filter_recent(table: etl.Table, lookback_min: int = 15) -> etl.Table:
    """
    Take a Petl table with a 'timestamp' column, convert it to int,
    and keep only rows within the last `lookback_min` minutes.
    """
    cutoff = int(time.time()) - lookback_min * 60
    tbl_int = etl.convert(table, 'timestamp', int)
    return etl.select(tbl_int, "{timestamp} >= %d" % cutoff)

def expand_demo_rows(single_row: etl.Table, n: int = 5, dt: int = 60) -> etl.Table:
    """
    For tutorial demos: clone a single-row table into `n` rows,
    each offset by `dt` seconds, then sort by timestamp ascending.
    """
    original = next(iter(etl.dicts(single_row)))
    clones = []
    for i in range(n):
        clone = dict(original)
        clone['timestamp'] -= i * dt
        clones.append(clone)
    multi = etl.fromdicts(clones).sort('timestamp')
    return multi
