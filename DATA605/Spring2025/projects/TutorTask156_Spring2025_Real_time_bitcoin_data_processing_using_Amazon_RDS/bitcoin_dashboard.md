# Bitcoin Dashboard

## Overview

The Bitcoin Dashboard is an interactive web application built with Streamlit that visualizes real-time and historical Bitcoin price data from the Amazon RDS database. The dashboard provides a user-friendly interface to monitor Bitcoin price trends, moving averages, and trading volume.

## Features

- **Real-time Bitcoin Price**: View the most recent Bitcoin price from the database
- **Historical Price Trends**: Visualize Bitcoin price changes over a customizable time period
- **Technical Analysis**: View multiple moving averages (5-day, 10-day, 20-day) plotted alongside price data
- **Trading Volume Analysis**: Examine Bitcoin trading volume over time
- **Adjustable Time Range**: Customize the analysis period using a slider (1-60 days)

## Getting Started

### Prerequisites

- Docker and Docker Compose installed
- Amazon RDS PostgreSQL database configured with Bitcoin price data
- Environment variables set up for database connection

### Running the Dashboard

The dashboard can be launched using Docker:

```bash
cd docker_data605_style
./docker_streamlit.sh
```

Then access the dashboard at: http://localhost:8080

Alternatively, run both Jupyter and Streamlit together:

```bash
cd docker_data605_style
./docker_start_all.sh
```

### Using the Dashboard

1. **Adjust Time Range**: Use the sidebar slider to select the number of days for analysis (1-60 days)
2. **View Key Metrics**: The dashboard displays the latest Bitcoin price and the lowest price over the selected period
3. **Explore Price Trends**: The line chart shows Bitcoin price movement over time
4. **Analyze Moving Averages**: Technical analysis chart displays price with 5, 10, and 20-day moving averages
5. **Monitor Trading Volume**: Bar chart shows trading volume over the selected period

## Technical Details

### Data Sources

The dashboard connects directly to the Amazon RDS PostgreSQL database and retrieves:
- Latest Bitcoin price from the `raw_bitcoin_prices` table
- Historical price data for the selected time period
- Trading volume data for the selected time period

### Components

1. **Metrics Display**:
   - Latest Bitcoin price
   - Lowest price over the selected period

2. **Price Chart**:
   - Interactive line chart showing Bitcoin price over time
   - Hover functionality to see precise values

3. **Moving Averages**:
   - Multi-line chart with price and moving averages
   - 5-day MA always displayed
   - 10-day MA displayed when range ≥ 10 days
   - 20-day MA displayed when range ≥ 20 days

4. **Volume Chart**:
   - Bar chart showing daily trading volume
   - Helps identify periods of high market activity

### Implementation Details

The dashboard implementation uses:
- Streamlit for the web interface
- Plotly for interactive data visualization
- Pandas for data manipulation
- PostgreSQL queries for efficient data retrieval
- Moving average calculations for technical analysis

## Example Use Cases

1. **Short-term Analysis**: Set the slider to 7-14 days to analyze recent price movements and identify short-term trends
2. **Technical Trading Signals**: Use the moving averages to identify potential buy/sell signals when lines cross
3. **Volume Analysis**: Identify correlation between price movements and trading volume
4. **Support/Resistance Identification**: Use longer time periods to identify key price levels

## Troubleshooting

- **No Data Displayed**: Verify database connection and ensure data exists for the selected period
- **Missing Moving Averages**: Some moving averages require minimum days of data (e.g., 20-day MA needs at least 20 days selected)
- **Performance Issues**: Consider reducing the time range if the dashboard is slow to load 