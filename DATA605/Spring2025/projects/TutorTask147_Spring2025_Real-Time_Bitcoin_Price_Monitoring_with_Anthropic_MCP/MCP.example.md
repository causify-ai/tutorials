# Bitcoin Price Monitor with FastMCP

## Table of Contents
- [Introduction](#introduction)
- [Architecture Overview](#architecture-overview)
- [Key Components](#key-components)
  - [1. FastMCP](#1-fastmcp)
  - [2. MCP_utils Helper Library](#2-mcp_utils-helper-library)
  - [3. Real-Time Price Resource](#3-real-time-price-resource)
  - [4. Trend Analysis Endpoint](#4-trend-analysis-endpoint)
  - [5. Threshold Alert Workflow](#5-threshold-alert-workflow)
  - [6. Price Visualization Tool](#6-price-visualization-tool)
- [Summary](#summary)

## Introduction

MCP.example.ipynb is a fully-worked example that shows how to build a real-time Bitcoin price monitor on top of FastMCP—a super-light API layer that turns ordinary Python functions into HTTP endpoints with a single decorator.

The notebook demonstrates how to:
- Fetch live data from the CoinGecko public API
- Wrap the data-fetching, analysis, and visualization logic behind easy-to-consume read-only resources
- Push price updates, trend summaries, and HTML plots to any client that can speak HTTP or WebSocket
- Run everything locally or inside Docker, with zero extra web-framework boilerplate

## Architecture Overview

```
┌──────────────────────┐        HTTP/WebSocket         ┌──────────────────┐
│  Jupyter Notebook    │  ◀────────────────────────── ▶│   Any Client     │
│  (Business Logic)    │                               │  (browser, curl) │
└──────┬───────────────┘                               └──────────────────┘
       │  FastMCP registers decorated callables
┌──────▼───────────────┐
│      FastMCP         │  Exposes JSON + streaming APIs for every resource
└──────────────────────┘
```

## Key Components

### 1. FastMCP

A micro-framework that scans for `@mcp.resource` decorators and spins up a hyper-fast ASGI server.
- Zero Config – no routing tables or Flask apps to write
- Async-First – native async def support lets you await network I/O directly
- Auto Docs – every endpoint is served with an OpenAPI spec at /docs

```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("bitcoin_monitor")
```

### 2. MCP_utils Helper Library

A thin wrapper around the CoinGecko REST endpoints. Keeps the notebook tidy and testable.

```python
async def get_price() -> float:
    url = f"{BASE_URL}/simple/price?ids=bitcoin&vs_currencies=usd"
    return (await httpx.get(url)).json()["bitcoin"]["usd"]
```

### 3. Real-Time Price Resource

Returns the most recent BTC price in USD.

```python
@mcp.resource("/price")
async def price() -> float:
    return await get_price()
```

### 4. Trend Analysis Endpoint

Aggregates the last 7 days of hourly candles and returns direction (up, down, flat) plus the percentage change.

```python
@mcp.resource("/trend")
async def trend() -> dict[str, Any]:
    df = await get_ohlc(days=7)
    pct = (df.close.iloc[-1] / df.close.iloc[0] - 1) * 100
    direction = "up" if pct > 1 else "down" if pct < -1 else "flat"
    return {"pct_change": pct, "direction": direction}
```

### 5. Threshold Alert Workflow

If the price swings more than $THRESHOLD USD in either direction, a server-sent event (SSE) is emitted so UI dashboards or bots can react instantly.

```python
@mcp.event("/alerts")
async def alerts(stream):
    last = await get_price()
    while True:
        await asyncio.sleep(10)
        current = await get_price()
        if abs(current - last) > THRESHOLD:
            await stream.send({"price": current, "delta": current - last})
            last = current
```

### 6. Price Visualization Tool

Generates a self-contained bitcoin_price.html file using Plotly so clients can embed an interactive chart without needing Python.

```python
@mcp.resource("/chart")
async def chart() -> bytes:
    html_path = await plot_price()
    return Path(html_path).read_bytes()
```

## Summary

This example demonstrates how to build a comprehensive Bitcoin price monitoring system using FastMCP. The implementation showcases several key capabilities:

1. **Real-time Data Access**: Fetching current Bitcoin prices from external APIs
2. **Data Analysis**: Processing price data to detect trends and significant changes
3. **Event-based Notifications**: Alerting clients when prices cross predefined thresholds
4. **Visualization**: Generating interactive charts for data exploration

The FastMCP framework makes it easy to expose these capabilities as HTTP endpoints with minimal boilerplate code. By decorating regular Python functions, we create a fully functional API that can be consumed by any client capable of making HTTP requests.

This architecture is highly extensible - you can add new endpoints for additional cryptocurrencies, implement more sophisticated analysis algorithms, or integrate with other data sources by simply adding new decorated functions.

For production deployments, the entire system can be containerized using Docker, ensuring consistent behavior across different environments while maintaining the simplicity of the core implementation.



