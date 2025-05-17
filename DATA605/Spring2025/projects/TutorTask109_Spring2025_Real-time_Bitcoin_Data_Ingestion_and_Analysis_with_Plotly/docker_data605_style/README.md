# Real-Time Bitcoin Blockchain Metrics Visualization and Time Series Analysis with Plotly

**Author:** Varun Parashar  
**Supervisor:** Adj. Prof. Giacinto Paolo Saggese  
**GitHub:** [Varun-22](https://github.com/Varun-22)  
**UMD Email:** vparasha@umd.edu  
**UID:** 121302922

---

## Description

This project presents a real-time visualization and time series analysis system for Bitcoin blockchain metrics using Python, Plotly, and Docker. The system collects live data from the Blockchain.com API at fixed intervals and tracks three core indicators: **Transaction Count**, **Hash Rate**, and **Block Size**. These metrics are processed into time series and visualized with interactive charts to monitor blockchain activity and understand long-term behavior using statistical decomposition.

---

## Plotly-Based Real-Time Bitcoin Blockchain Metrics Analysis

The system is built in Python and designed to run continuously by fetching updated metrics every 15 seconds. It uses Plotly for interactive visualizations, pandas for time series handling, and `statsmodels` for decomposing trends and seasonality. Docker is used to containerize the environment and ensure smooth, repeatable deployment across platforms.

---

## Process Overview

### Data Ingestion: `Bitcoin_API.py`

This script uses the `requests` library to fetch live blockchain data from the Blockchain.com public API. A dictionary maps each metric name to its respective endpoint, and data is converted into pandas DataFrames with proper datetime formatting. The script is modular and reusable for time series data from other APIs as well.

### Time Series Visualization: `Real_Time_Analysis_Using_PLOTLY.py`

This script contains the `BitcoinMetricsAnalyzer` class, which handles:
- Live data fetching using multithreading
- Appending new data points to each metric
- Time series plotting using `plotly.graph_objs`
- Decomposing each series into trend, seasonal, and residual components using `seasonal_decompose`

Two sets of visuals are generated:
- **Metric Time Series**: Multi-line chart of all three metrics over time.
- **Decomposed Time Series**: Visual breakdowns for each metric to analyze temporal patterns.

All outputs are saved as standalone `.html` files and viewable in a browser.

---

## Interactive Widgets

The Jupyter Notebook version includes interactive controls using `ipywidgets`. These allow users to start or pause live updates, select specific metrics, and control the update interval, making the notebook more user-friendly for presentations or educational use.

---

## HTML Export

All generated plots are exported as HTML files:
- `bitcoin_metric_plot.html` – Combined line chart of all metrics.
- `bitcoin_transaction_plot.html`, `bitcoin_hashrate_plot.html`, etc. – Individual decomposed plots.
These files are saved to the `output` directory and remain available after execution ends.

---

## Docker Implementation

To ensure consistent execution across systems, the project is containerized using Docker:
- The `Dockerfile` sets up a Python 3.7 environment and installs dependencies including `pandas`, `plotly`, and `statsmodels`.
- Scripts like `docker_build.sh`, `docker_exec.sh`, `docker_clean.sh`, and `run_jupyter.sh` help automate container lifecycle tasks.
- Volumes `/input` and `/output` are mounted to manage data flow between host and container.

---

## Key Observations and Insights

- Metrics like duration and transaction count show strong variations and contribute significantly to the decomposed visualizations.
- Hash rate exhibits visible periodic patterns, likely reflecting network mining behavior.
- Exported charts help preserve insights even after live analysis ends.
- Multithreading ensures continuous updates without interruption or data corruption.

---

## Project Structure

| File/Folder                                       | Description |
|--------------------------------------------------|-------------|
| `Bitcoin_API.py`                                 | Fetches real-time Bitcoin metrics from the Blockchain.com API |
| `Bitcoin_API.ipynb`                              | Jupyter Notebook version of the API fetch script |
| `Bitcoin_API.py.md` / `.ipynb.md`                | Markdown documentation versions of the API script |
| `Bitcoin_API.py_Markdown.ipynb`                  | Annotated notebook for explanation and review |
| `Real_Time_Analysis_Using_PLOTLY.py`             | Real-time visualization and time series decomposition script |
| `Real_Time_Analysis_Using_PLOTLY.ipynb`          | Notebook version of the main analysis script |
| `Real_Time_Analysis_Using_PLOTLY.py.md` / `.ipynb.md` | Markdown versions for documentation or review |
| `Dockerfile`                                     | Defines the environment for containerized execution |
| `requirements.txt`                               | Lists Python dependencies for local or Docker setup |
| `docker_build.sh` / `docker_exec.sh` / `docker_clean.sh` | Shell scripts to automate Docker image and container management |
| `docker_push.sh` / `docker_bash.sh`              | Scripts for Docker image upload and terminal access |
| `run_jupyter.sh`                                 | Launches Jupyter Notebook inside the Docker container |
| `install_jupyter_extensions.sh`                  | Installs additional notebook extensions inside Docker |
| `version.sh`, `docker_build.version.log`         | Docker version management and logs |
| `bitcoin_metric_plot.html` / `bitcoin_transaction_plot.html` | Exported HTML plots for interactive metric visualization |
| `bitcoin_metrics_analysis_*.html`                | Timestamped exports of metric analysis sessions |
| `__pycache__/`                                   | Auto-generated Python cache directory |
| `tmp.build/`                                     | Temporary build directory used during Docker operations |

---

## Setup Instructions

### Local (Without Docker)
```bash
git clone https://github.com/Varun-22/Real-Time-Bitcoin-Blockchain-Plotly.git
cd Real-Time-Bitcoin-Blockchain-Plotly
pip install -r requirements.txt
python Real_Time_Analysis_Using_PLOTLY.py
```

### Using Docker
```bash
./docker_build.sh       # Build image
./docker_exec.sh        # Run container interactively
./run_jupyter.sh        # Launch Jupyter in container
```

---

## Conclusion

This project delivers a complete and modular system for collecting, analyzing, and visualizing real-time Bitcoin blockchain metrics. By combining API integration, time series decomposition, and interactive Plotly charts, the platform enables efficient monitoring of blockchain network activity. Docker ensures reliable execution across diverse environments, and HTML export supports long-term analysis and sharing. The project serves as a scalable base for extending to advanced analytics such as anomaly detection or forecasting.
