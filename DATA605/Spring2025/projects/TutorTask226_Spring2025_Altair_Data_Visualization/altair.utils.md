# Altair_utils.py

## Overview

This module defines reusable utility functions to process, transform, and analyze the raw Bitcoin market data before visualization.

## Key Functions

- `calculate_rsi(prices)`: Calculates Relative Strength Index for momentum analysis.
- `bollinger_bands(prices)`: Computes Bollinger Bands to assess volatility.
- `volatility_surface(df)`: Prepares time-window based volatility heatmap data.
- `prepare_mempool_data()`: Formats mempool data into size distribution plots.

## Architecture Role

Decouples analytical logic and data transformation from the API layer, promoting modularity and reuse across endpoints.
