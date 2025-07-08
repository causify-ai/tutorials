## Example Application: Real-Time Bitcoin Pipeline

### Architecture Overview

The full pipeline flow is:

1. Fetch live Bitcoin prices from the CoinGecko API.
2. Log timestamped prices into a Snowflake-hosted table (`BTC_PRICES`).
3. Periodically query and visualize the data.
4. Analyze trends using moving averages and volatility indicators.

All processing is performed in Python using Jupyter notebooks and pushed via Snowflake’s Python connector.

### Data Source: CoinGecko

The `fetch_bitcoin_price()` function calls CoinGecko’s REST API endpoint:

It retrieves the most recent USD value of 1 Bitcoin.

### Snowflake Database Integration

Using `snowflake-connector-python`, we:

- Securely connect via `.env` credentials.
- Create or re-use the `BTC_PRICES` table.
- Insert price records with UTC timestamps.
- Use SQL queries to retrieve results for visualization and analysis.

Key functions:
- `connect_to_snowflake()`
- `create_btc_table()`
- `insert_bitcoin_price()`
- `fetch_btc_data()`

### Streaming and Logging Loop

To simulate streaming:

- A logging loop collects price every 10 seconds (`time.sleep(10)`).
- Each entry is inserted into Snowflake via the connector.
- After 5 cycles, the latest data is fetched and visualized.

This helps simulate real-time ingestion with minimal overhead.

### Time Series Analysis and Visualization

The fetched data is used to:

- Plot the raw prices using `matplotlib`.
- Compute a 3-point Simple Moving Average (SMA) to smooth noise.
- Measure rolling standard deviation (volatility).

This illustrates how Snowflake + Python can power quick exploratory analysis of crypto time series.

## Conclusion

This example bridges real-world API data (CoinGecko) with Snowflake storage and analytics.

You now have:
- A streaming Bitcoin logger.
- A Snowflake backend for persistence.
- Plots and analytics generated in real-time.

This setup can be scaled for larger data, more coins, or extended to dashboards (e.g., with Plotly Dash or Power BI).

