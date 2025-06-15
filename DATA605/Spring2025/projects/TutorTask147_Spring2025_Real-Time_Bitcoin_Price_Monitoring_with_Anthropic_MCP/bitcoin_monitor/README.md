# Bitcoin Price Monitoring System

## System Overview

The Bitcoin Price Monitoring System is a comprehensive solution for tracking and analyzing Bitcoin prices in real-time. It consists of two main components:

1. **MCP Server**: Handles data processing, API interactions, and analysis
2. **MCP Client**: Provides a natural language interface through Claude AI

### Key Features

- **Real-time Price Monitoring**: Live Bitcoin price tracking via CoinGecko API
- **Price Alerts**: Automated alerts for significant price movements
- **Trend Analysis**: Advanced price trend prediction using SARIMAX models
- **Interactive Visualizations**: Dynamic price charts with moving averages
- **Natural Language Interface**: Query the system using plain English
- **Comprehensive Market Analysis**: Detailed summaries and forecasts

### Available Tools

1. `get_price`: Current Bitcoin price in USD
2. `get_ohlc`: Open/High/Low/Close data
3. `get_history`: Historical market data
4. `alert_price_change`: Price movement alerts
5. `detect_trend`: Price trend analysis
6. `plot_price`: Interactive price charts
7. `get_summary`: Market summaries

## Prerequisites

1. Docker and Docker Compose installed on your system
2. An Anthropic API key for Claude
3. Python 3.10+ (if running without Docker)
4. Internet connection for real-time data

## Setup Instructions

### 1. File Structure

Ensure your project directory has the following files:

```
bitcoin-monitor/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
├── MCP.server.py    (MCP server script)
├── MCP.client.py    (MCP client script)
├── setup.sh
└── run.sh
```

### 2. Set Up Your Environment

1. Make the setup and run scripts executable:

```bash
chmod +x setup.sh run.sh
```

2. Run the setup script to prepare your environment:

```bash
./setup.sh
```

3. Edit the `.env` file with your Anthropic API key:

```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

### 3. Run the Bitcoin Monitor

Start the Bitcoin Monitor in interactive mode:

```bash
./run.sh
```

This will launch the Docker container with your Bitcoin Monitor system.

## How It Works

### System Architecture

- **MCP Server**:
  - Fetches real-time data from CoinGecko API
  - Processes and analyzes price trends
  - Generates interactive visualizations
  - Manages data storage and caching
  - Implements error handling and rate limiting

- **MCP Client**:
  - Provides natural language interface
  - Communicates with Claude AI
  - Processes user queries
  - Manages tool execution
  - Handles error reporting

### Data Flow

1. User submits a query through the client
2. Claude AI interprets the query
3. Client executes appropriate tools on the server
4. Server processes the request and returns results
5. Results are formatted and presented to the user

### Data Storage

- Price charts are saved in `bitcoin_monitor` directory
- Files are timestamped to prevent overwrites
- Data persists between container runs
- Automatic cleanup of old data


### Running in Background Mode

To run the container in the background, use:

```bash
docker-compose up -d
```

And connect to the interactive shell with:

```bash
docker exec -it bitcoin-monitor bash
```

### Viewing Logs

If running in background mode, view logs with:

```bash
docker-compose logs -f
```

## Example Queries

The system understands various types of queries:
- "What's the current Bitcoin price?"
- "Show me a price chart for the last 7 days"
- "Analyze the price trend for the next day"
- "Has there been any significant price movement recently?"
- "Give me a full market summary"

## Troubleshooting

### API Key Issues

If you see authentication errors, ensure your API key in the `.env` file is correct.

### Container Crashes

Check the logs with `docker-compose logs` to see what went wrong.


### Rate Limiting

The system implements automatic retry logic for API rate limits. If you see rate limit warnings, the system will automatically wait and retry.

