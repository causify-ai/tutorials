# Bitcoin Price Monitoring MCP Server

## Overview

The Bitcoin Price Monitoring MCP Server is a real-time cryptocurrency monitoring system built using the FastMCP framework. It provides a suite of tools for tracking Bitcoin prices, analyzing trends, and generating visualizations.

### Key Features

- **Real-time Price Monitoring**: Fetches current Bitcoin prices from CoinGecko API
- **Price Alerts**: Monitors significant price changes and triggers alerts
- **Trend Analysis**: Uses SARIMAX models to predict price trends
- **Interactive Visualizations**: Generates interactive Plotly charts with:
  - Price history
  - Moving averages (7-day and 30-day)
  - Customizable time ranges (1-365 days)
- **Comprehensive Summaries**: Provides detailed market snapshots including:
  - Current price
  - 24-hour changes
  - Trend forecasts
  - Confidence intervals

### Available Tools

1. `get_price`: Returns current Bitcoin price in USD
2. `get_ohlc`: Retrieves Open-High-Low-Close data
3. `get_history`: Gets historical market data for specific dates
4. `alert_price_change`: Monitors price changes and triggers alerts
5. `detect_trend`: Analyzes price trends using ARIMA models
6. `plot_price`: Generates interactive price charts
7. `get_summary`: Provides comprehensive market summaries

### Data Storage

- Price charts are saved in a `plots` directory
- Files are timestamped to prevent overwrites
- HTML format for interactive viewing

# Running Bitcoin MCP Server for Claude Desktop

This guide shows how to run our Bitcoin Monitor MCP server in Docker for use with Claude Desktop.

## Setup Instructions

### 1. Create the Docker image

Create a `Dockerfile.server` with the provided content, then build the image:

```bash
docker build -f Dockerfile.server -t bitcoin-mcp-server .
```

### 2. Create a wrapper script for Claude Desktop

Claude Desktop needs a command to execute.

Make it executable:
```bash
chmod +x bitcoin-mcp-docker.sh
```

### 3. Configure Claude Desktop

Add the following to your Claude Desktop configuration file:
- Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "bitcoin-monitor": {
      "command": "/full/path/to/bitcoin-mcp-docker.sh",
      "args": [],
      "env": {}
    }
  }
}
```

**Important**: Replace `/full/path/to/bitcoin-mcp-docker.sh` with the actual absolute path to your wrapper script.

### 4. Alternative: Direct Docker Command

If you prefer to avoid the wrapper script, you can configure Claude Desktop to run Docker directly:

```json
{
  "mcpServers": {
    "bitcoin-monitor": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "bitcoin-mcp-server"],
      "env": {}
    }
  }
}
```

## Troubleshooting

### Docker Permission Issues
- On Linux, you might need to add your user to the docker group: `sudo usermod -aG docker $USER`
- Log out and back in for changes to take effect

### Testing the Server
Test if the server runs correctly:
```bash
./bitcoin-mcp-docker.sh
```
You should see MCP server output. Press Ctrl+C to exit.

### Claude Desktop Not Finding Server
- Ensure the path in your config is absolute, not relative
- Check Claude Desktop logs for error messages
- Verify Docker is running: `docker ps`

### Windows-Specific Issues
On Windows with WSL2:
- Use WSL paths in the config file if running Docker in WSL
- Ensure Docker Desktop is set to use WSL2 backend
