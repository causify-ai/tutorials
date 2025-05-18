# Real-Time Bitcoin Price Analysis using Docker SDK for Python

## Project Overview

This project demonstrates how to build a real-time data ingestion and analysis pipeline for Bitcoin price data using the Docker SDK for Python.  
It features:
- Programmatic management of Docker containers for databases (InfluxDB)
- Real-time BTC price ingestion and storage
- End-to-end analytics and visualization in Jupyter Notebooks

## Getting Started

### Prerequisites

- Docker installed and running (Docker Desktop or equivalent)
- Python 3.8+ (used in container)
- A valid InfluxDB admin token, org, and bucket (set via `.env`)

1.5. **Install Python dependencies** (optional if running outside container):
   ```bash
   pip install -r requirements.txt
   ```

1.6. **Make the pipeline script executable (first time only):**
   ```bash
   chmod +x run_pipeline.sh
   ```

### Setup and Run

##  Running the Project (Automated Script)

To streamline the setup process, this project includes a shell script: `run_pipeline.sh`.

This script:
- Builds the Docker image (`bitcoin_realtime_sdk`)
- Launches the real-time BTC price analysis pipeline using Docker SDK

###  How to Use

```bash
chmod +x run_pipeline.sh  # First-time only: Make script executable
./run_pipeline.sh         # Runs the entire pipeline
## Automated Pipeline (Recommended)

To run the full project pipeline with a single command, use the provided shell script:

```bash
./run_pipeline.sh
```

## Environment Variables

Before running the project, you need to create a `.env` file in your root directory with the following content:

```bash
INFLUXDB_USERNAME=admin;
INFLUXDB_PASSWORD=adminpassword;
INFLUXDB_ORG=data-605;
INFLUXDB_BUCKET=crypto-bucket;
INFLUXDB_ADMIN_TOKEN=As1W8vixBZwzD3dDvmrAvZi79sx1QdyAXH0H73FShCxVfOf4hBWHPwa5osmXkw6r;
INFLUXDB_URL=http://influxdb:8086;

This will:
- Build the BTC fetcher Docker image if not already built
- Start all required containers (InfluxDB, Grafana, BTC Fetcher) using the Docker SDK
- Automatically fetch and stream real-time BTC data into InfluxDB
- Load the Grafana dashboard with auto-refreshing visualizations
- Clean up containers when done

## Environment Variables & Security

This project uses environment variables for all sensitive credentials. Copy `.env.example` to `.env` and fill in your values. Never commit secrets to version control.

## Troubleshooting

- If InfluxDB or Grafana containers fail to start, ensure Docker is running and ports 8086/3000 are free.
- If you see authentication errors, check your environment variables for typos.
- For Mac/Windows, if containers can't communicate, try using `network_mode="bridge"` instead of `host` in Docker SDK calls.

## Expected Outputs

- InfluxDB and Grafana containers running
- Bitcoin data fetched and stored in InfluxDB
- Plot saved to `output/btc_analysis.png`
- Grafana auto-provisioned with a working dashboard
- Screenshot of Grafana showing live BTC price data (optional for README)
- Live-updating BTC line chart in Grafana
- Real-time data ingestion logs printed to terminal

## Data Pipeline Diagram

```mermaid
graph TD
    A[CryptoCompare API] --> B[BTC Fetcher (Python)]
    B --> C[InfluxDB (Docker)]
    C --> D[Jupyter Notebook]
    C --> E[Grafana (Docker)]
```

## API Choice

This project uses CryptoCompare for BTC price data due to its simple free API. CoinGecko can be added with minor changes if needed.

## Grafana Dashboard Setup

Grafana is provisioned automatically with:

- A data source for InfluxDB
- A dashboard panel for BTC close price
- The dashboard uses Flux query to visualize real-time BTC close price from the `crypto_prices` measurement
Accessible at: [http://localhost:3000](http://localhost:3000) (default login: admin/admin)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by the need to monitor Bitcoin prices in real-time.
- Powered by open-source technologies: Python, Docker, InfluxDB, Grafana.