<!-- toc -->

- [Project Overview](#project-overview)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
  - [Docker (Recommended)](#docker-recommended)
  - [Local Python Environment](#local-python-environment)
- [Usage](#usage)
  - [API Notebook](#api-notebook)
  - [Example Notebook](#example-notebook)
- [Key Components](#key-components)
  - [bitcoin_petl_utils.py](#bitcoin_petl_utilspy)
  - [Notebooks](#notebooks)
  - [Markdown Documentation](#markdown-documentation)
- [Dependencies](#dependencies)
- [Data Sources & Services](#data-sources--services)
- [Contributing](#contributing)

<!-- tocstop -->

# Project Overview

**Real-Time Bitcoin Price Analysis with Petl**  
This project demonstrates how to build a fully reproducible, local data ingestion and processing pipeline for Bitcoin prices using Python and the Petl library. The goal is to fetch live price data from a public API, perform ETL transformations, execute time series analyses, and visualize results—both statically and interactively—all within a Docker container or local environment. 

Learners will gain experience in:
- Continuous data ingestion and storage
- Tabular ETL workflows with Petl
- Time series analysis using pandas and Statsmodels
- Static and interactive plotting (Matplotlib, Seaborn, Plotly)
- Modular code organization and documentation

# Project Structure

```
TutorTask354_Spring2025_Real_Time_Bitcoin_Price_Analysis_with_Petl/
├── bitcoin_petl_utils.py       # ETL utility module with helper functions
├── BitcoinPetl.API.ipynb        # Notebook demonstrating API usage
├── BitcoinPetl.example.ipynb    # End-to-end example notebook
├── BitcoinPetl.API.md           # Markdown documentation for API layer
├── BitcoinPetl.example.md       # Markdown outline of example workflow
├── docker_common/
│   ├── docker_build.sh          # Script to build Docker image
│   ├── docker_bash.sh           # Script to launch container shell
│   └── docker_jupyter.sh        # Script to start Jupyter Notebook
└── README.md                    # This file
```

# Setup & Installation

## Docker (Recommended)

1. **Build the Docker image**  
   ```bash
   bash docker_common/docker_build.sh
   ```
2. **Start an interactive shell**  
   ```bash
   bash docker_common/docker_bash.sh
   ```
   This mounts the project directory at `/work` inside the container.

3. **Launch Jupyter Notebook**  
   ```bash
   bash docker_common/docker_jupyter.sh
   ```
   Open your browser at `http://localhost:8888` and navigate to `BitcoinPetl.API.ipynb` or `BitcoinPetl.example.ipynb`.

## Local Python Environment

1. **Clone the repo** and navigate to your project folder.
2. **Install dependencies**:
   ```bash
   pip install requests petl pandas matplotlib seaborn statsmodels plotly jupyterlab
   ```
3. **Launch Jupyter**:
   ```bash
   jupyter lab
   ```
4. Open the notebooks in the `projects/TutorTask354_*` directory.

# Usage

## API Notebook

- Demonstrates core functions in `bitcoin_petl_utils.py`:
  - Fetch live and historical Bitcoin prices
  - Expand single-row data for demos
  - Apply Petl transformations: convert, rename, sort, filter
  - Compute rolling indicators and alerts
  - Convert Petl tables to pandas DataFrames

## Example Notebook

- End-to-end pipeline:
  1. Initialize or reset CSV storage
  2. Demo ETL transformations
  3. Continuous ingestion loop (append data every 30 seconds)
  4. Pandas analysis: moving averages, volatility
  5. Static plots (Matplotlib, Seaborn)
  6. Seasonal decomposition (Statsmodels)
  7. Interactive Plotly dashboard with live refresh

# Key Components

## bitcoin_petl_utils.py

- **fetch_btc_price_table()**: Fetches the latest Bitcoin price via CoinGecko API
- **fetch_historical_range()**: Retrieves historical price data over a time range
- **expand_demo_rows()**: Generates demo tables from single rows
- **filter_recent()**: Filters tables by recency
- **compute_indicators()**: Adds moving average & volatility columns
- **alert_on_threshold()**: Filters rows exceeding a price threshold
- **init_csv() / append_price() / load_dataframe() / add_indicators()**: File-based I/O helpers

## Notebooks

- **BitcoinPetl.API.ipynb**: Focused on API usage and simple table transforms
- **BitcoinPetl.example.ipynb**: Full tutorial with ingestion, analysis, and visualization

## Markdown Documentation

- **BitcoinPetl.API.md**: Detailed API reference and examples
- **BitcoinPetl.example.md**: Step-by-step guide for the example notebook flow

# Dependencies

- Python 3.8+  
- `requests`  
- `petl`  
- `pandas`  
- `matplotlib`  
- `seaborn`  
- `statsmodels`  
- `plotly`  
- Jupyter Lab/Notebook

# Data Sources & Services

- **CoinGecko API** (`https://api.coingecko.com/api/v3/simple/price` and `/market_chart/range`)  
  Free, no-auth required for basic rate limits. Provides current and historical BTC/USD pricing.