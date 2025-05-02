# Real‑Time Bitcoin Price Monitoring with Anthropic MCP

A Dockerized MCP server and client toolkit that fetches live and historical Bitcoin data via the CoinGecko API, exposes it as MCP resources and tools, runs automated threshold alerts and time‑series trend analysis, and generates interactive visualizations.

---

## Features

- **MCP Resources & Tools**  
  - `crypto://price` – current BTC price in USD  
  - `get_ohlc(days)` – OHLC data for the past N days  
  - `get_history(date)` – historical snapshot for a given date  
  - `alert://price_change` – automatic threshold alerts  
  - `detect_trend(days)` – ARIMA‑based trend forecast  
  - `plot_price(days)` – saves a Plotly HTML chart  

- **Data Processing**  
  - Real‑time ingestion via CoinGecko’s REST API :contentReference[oaicite:0]{index=0}  
  - Time‑series analysis with Pandas & Statsmodels  
  - Interactive plotting with Plotly  

- **Containerized Deployment**  
  - Dockerfile for reproducible environments  
  - STDIO and TCP transports supported  

- **CLI Demonstration**  
  - Self‑contained Python script to exercise all endpoints  

---

## Prerequisites

- **Docker** (version 20.10+)  
- **Python** 3.10+ (for local dev)  
- Internet access to `api.coingecko.com`  

---