# Altair_API.py

## Overview

This file defines the FastAPI application and the major API endpoints for interacting with Bitcoin market data and visualization components.

## Key Endpoints

- `GET /historical`: Returns historical Bitcoin price data using `yfinance`.
- `GET /live`: Streams real-time price updates via WebSocket.
- `GET /volatility`: Computes and returns the volatility surface.
- `GET /mempool`: Visualizes mempool transaction size distribution.

## Architecture Role

Acts as the core backend interface for data input/output, interfacing directly with the utility layer and returning Altair specs or JSON.
