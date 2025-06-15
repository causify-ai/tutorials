# Real-Time Bitcoin Data Processing with Datasette

A dynamic web-based dashboard to visualize and analyze real-time Bitcoin price trends using SQLite, Datasette, and the CoinGecko API.

---

## Project Structure

```
TutorTask99_Spring2025_Real-Time_Bitcoin_Data_Processing_with_Datasette/
│
├── data/                          # Contains the SQLite database and CSV snapshots
│   ├── bitcoin_data.db            # Main SQLite database storing BTC prices
│   └── bitcoin_prices_*.csv       # Optional historical export
│
├── scripts/                       # Python scripts for data ingestion and processing
│   ├── fetch_bitcoin_data.py      # Fetches BTC data from the CoinGecko API
│   └── save_to_sqlite.py          # Saves cleaned data to SQLite
│
├── docker_data605_style/         # Docker environment setup and service scripts
│   ├── Dockerfile                 # Custom Docker image definition
│   ├── run_jupyter.sh             # Launches Jupyter with Datasette
│   └── run_services.sh            # Runs BTC data update script
│   └── requirements.txt           # Python dependencies
│
├── static/                        # Custom styling and assets
│   ├── custom.css                 # Styled CSS for Datasette theme
│   └── logo.png                   # Logo for branding
│
├── bitcoin_utils.py              # Shared utility functions (fetch, save, clean)
├── bitcoin.API.ipynb             # Notebook showcasing API fetch and update
├── bitcoin.example.ipynb         # Main notebook for visualization and analysis
├── metadata.json                 # Datasette configuration, queries, dashboard layouts
├── README.md                     # You're here
└── __init__.py                   # Init file (for modularization)
```

---

## Features

- Live BTC Price Updates: Pulls real-time Bitcoin prices from CoinGecko.
- Time-Series Dashboard: Interactive graphs using Vega-Lite inside Datasette.
- Custom KPIs: Includes max, min, and average price indicators.
- Z-Score & Trend Analysis: Detect anomalies and patterns.
- Dockerized Workflow: Fully contained reproducible setup.

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/real-time-bitcoin-datasette.git
cd real-time-bitcoin-datasette
```

### 2. Build Docker Image

```bash
cd docker_data605_style
./docker_build.sh
```

### 3. Run the Container

```bash
./docker_jupyter.sh
```

This starts:
- Jupyter Lab on http://localhost:8888
- Datasette on http://localhost:8001

---

## Dependencies

The following tools are used and installed via Docker:

- pandas
- requests
- sqlite3
- datasette
- datasette-vega
- datasette-dashboards
- matplotlib

If running locally, install manually with:

```bash
pip install -r docker_data605_style/requirements.txt
```

---

Once Downloaded

```bash
DOCKER_BUILDKIT=0 docker build --no-cache -t umd_data605/umd_data605_template .
```
```bash
./docker_jupyter.sh  
```

## Datasette Dashboards

- Bitcoin Visual Dashboard: http://localhost:8001/-/dashboards/bitcoin-visuals
- KPI Dashboard: http://localhost:8001/-/dashboards/bitcoin-kpis

---

## Credits

- Data Source: https://www.coingecko.com/
- Visualization Engine: https://datasette.io/
- Author: Your Name, MS Data Science, University of Maryland
