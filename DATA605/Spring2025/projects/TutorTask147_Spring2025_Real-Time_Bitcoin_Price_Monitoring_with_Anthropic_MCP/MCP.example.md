# Bitcoin Monitor

A Python script that monitors Bitcoin prices and provides analysis tools using the Managed Context Protocol (MCP) framework.

## Overview

This script creates an MCP server that offers several tools for monitoring and analyzing Bitcoin prices:
- Fetching current price data
- Retrieving historical OHLC data
- Getting historical market snapshots
- Price change alerts based on configurable thresholds
- Trend detection using time series analysis (ARIMA)
- Price visualization with Plotly

## Requirements

- Python 3.10+
- Dependencies:
  - requests
  - pandas
  - statsmodels
  - plotly
  - mcp (Managed Context Protocol)

## Usage

Run the script directly:

```bash
python MCP.exapmle.py
```

This will start the MCP server in stdio transport mode. The server exposes various tools and resources that can be accessed via MCP clients.

### Available Tools

| Tool | Description |
|------|-------------|
| `get_price()` | Returns the latest BTC price in USD |
| `get_ohlc(days=7)` | Returns OHLC data for the specified number of days |
| `get_history(date)` | Returns a BTC market snapshot for a specific date |
| `check_price_change(threshold=500.0)` | Monitors price changes and alerts if they exceed the threshold |
| `detect_trend(days=30)` | Fits an ARIMA model to predict price trends |
| `plot_price(days=7)` | Creates an interactive Plotly chart of BTC prices |

## Configuration

- `BASE_URL`: The CoinGecko API base URL
- `THRESHOLD`: The default USD price-change threshold for alerts (default: $500)

## API Documentation

For detailed documentation on the MCP framework and how to interact with this server, refer to the MCP documentation.

## Development


## Data Source

This script uses the CoinGecko API to fetch Bitcoin price data. No API key is required for the basic functionality used in this script.

## License

