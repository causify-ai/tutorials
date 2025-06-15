# Real‑Time Bitcoin Price Monitoring with Anthropic MCP

A comprehensive Bitcoin monitoring system that combines real-time data analysis, automated alerts, and interactive visualizations through the Anthropic MCP framework. This project is containerized for easy deployment and includes both server and client components.

## Project Structure

The project consists of several key components, each with its own detailed documentation:

- **Bitcoin Monitor** (`bitcoin_monitor/README.md`): Core monitoring system with real-time price tracking and analysis tools
- **MCP Server** (`MCP_server/README.md`): Server implementation for handling data processing and API interactions
- **Example Implementation** (`MCP.example.md`): Sample code and usage patterns
- **API Client** (`Coingecko.API.md`): Lightweight client for CoinGecko API integration

## Key Features

- **Real-time Monitoring**
  - Live Bitcoin price tracking via CoinGecko API
  - Automated price change alerts
  - Historical data analysis
  - Interactive price visualizations

- **Analysis Tools**
  - ARIMA-based trend forecasting
  - OHLC data analysis
  - Market summaries and insights
  - Customizable alert thresholds

- **Technical Features**
  - Dockerized deployment
  - MCP server and client architecture
  - Natural language interface through Claude AI
  - Comprehensive error handling and logging

## Getting Started

1. **Prerequisites**
   - Docker (version 20.10+)
   - Python 3.10+ (for local development)
   - Internet access to `api.coingecko.com`

2. **Setup and Running**
   For detailed setup instructions, please refer to:
   - `bitcoin_monitor/README.md` for the main monitoring system
   - `MCP_server/README.md` for server configuration
   - `MCP.example.md` for implementation examples

## Documentation

Each component has its own detailed README file with specific instructions:

- **Bitcoin Monitor**: Core system setup and usage
- **MCP Server**: Server configuration and deployment
- **Example Implementation**: Code examples and patterns
- **API Client**: CoinGecko API integration details


## References

- [CoinGecko API Documentation](https://www.coingecko.com/en/api)
- [Anthropic MCP Documentation](https://modelcontextprotocol.io/introduction)

