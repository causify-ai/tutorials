# Datasette & CoinGecko: Capabilities Overview

This document provides a structured overview of the key capabilities of **Datasette** and the **CoinGecko API**, facilitating informed decisions on their integration for data exploration, visualization, and analytics.

---

## 1. Datasette

Datasette is an open-source platform designed to turn SQLite databases into interactive, searchable web applications. Below are its primary features:

### 1.1 Data Publishing & Exploration

* **Instant Deployment**: Launch a web interface for any SQLite database with a single command.
* **Table Browsing**: Navigate tables, inspect rows, and view schema details.
* **Custom Queries**: Run ad-hoc SQL queries directly in the browser.
* **Faceted Search**: Filter data by column values using auto-generated UI filters.

### 1.2 User Interface Customization

* **Metadata Configuration**: Define database/table descriptions, labels, and canned queries via `metadata.json`.
* **Theming & Styling**: Inject custom CSS/JS to match branding and improve aesthetics.
* **Plugins & Extensions**:

  * **datasette-vega**: Embed interactive Vega-Lite charts.
  * **datasette-cluster-map**: Visualize geospatial data on maps.
  * **datasette-json-html**: Render JSON columns with collapsible trees.
  * **datasette-block-robots**: Control search engine indexing via `robots.txt`.

### 1.3 Dashboards & Visualizations

* **Built-in Charting**: Auto-generated charts for time series and numeric data.
* **Canned Queries**: Pre-defined SQL queries with display configuration (line, bar, scatter, etc.).
* **Dashboard Routes**: Create curated pages under `/-/dashboards/` with multiple chart panels.
* **Live Data Updates**: Integrate with scripts that append new records to SQLite, reflecting changes in real-time.

### 1.4 Security & Access Control

* **Read-Only Defaults**: Safe exploration without risk of data modification.
* **Authentication Plugins**: Add login mechanisms for private datasets.
* **Row-Level Permissions**: Restrict visibility on a per-row or per-user basis via plugins.

### 1.5 Scalability & Deployment

* **Lightweight**: Single binary, minimal dependencies.
* **Containerization**: Easily Dockerized for consistent deployment.
* **Serverless Options**: Host on Vercel, Netlify, or other platforms with SQLite support.

---

## 2. CoinGecko API

CoinGecko provides free and public access to cryptocurrency data without requiring an API key. Its endpoints cover a wide range of data needs:

### 2.1 Market Data

* **Current Prices**: Fetch real-time prices for multiple coins in various fiat and crypto currencies.
* **Market Capitalization**: Retrieve live market cap and 24h trading volume.
* **Price Change**: Obtain 24h/7d/30d percentage changes for price, market cap, and volume.

### 2.2 Historical Data

* **Market Charts**: Time series data for price, market cap, and volume over user-defined periods (e.g., 1, 7, 30, 90, 365 days).
* **OHLC**: Open-High-Low-Close data for candlestick charting at various intervals.
* **Historical Snapshots**: Retrieve data as of a specific date.

### 2.3 Asset Information

* **Coin List**: Comprehensive list of all supported coins with `id`, `symbol`, and `name`.
* **Coin Details**: Metadata including description, links, categories, and development/community metrics.
* **Tickers & Exchanges**: Real-time order book and trading pairs across multiple exchanges.

### 2.4 Global Metrics

* **Overall Market**: Total cryptocurrency market cap, 24h volume, BTC dominance, and market sentiment.
* **Derivative Data**: Futures, options, and perpetual contracts stats.

### 2.5 Developer-Friendly Features

* **No API Key**: Open access with generous rate limits.
* **RESTful Design**: Intuitive endpoints (`/simple/price`, `/coins/{id}/market_chart`, `/global`).
* **JSON Responses**: Easily consumed in Python, JavaScript, or any HTTP client.
* **Pagination & Filters**: Control response size and content via query parameters.

---

## 3. Integrating Datasette & CoinGecko

By combining Datasette with live data from CoinGecko, you can:

1. **Automate Ingestion**: Use scheduled scripts to fetch new prices and append to SQLite.
2. **Real-Time Dashboards**: Leverage Datasette’s `datasette-vega` plugin to plot up-to-the-minute charts.
3. **Canned Analysis**: Predefine queries (e.g., moving averages, volatility) and present them as interactive dashboards.
4. **Custom Branding**: Match your organization’s design with custom CSS and logos.
5. **Secure Sharing**: Publish read-only dashboards to stakeholders without exposing raw data or credentials.

---
