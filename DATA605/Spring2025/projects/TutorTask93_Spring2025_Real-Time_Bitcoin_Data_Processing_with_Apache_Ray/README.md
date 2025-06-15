# Real-Time Bitcoin Data Processing with Apache Ray

**Author**: Bala Swapnika Gopi 
**Date**: May 17, 2025  
**Course**: DATA605 — Spring 2025

---

## 1. Project Overview

This project builds an automated pipeline to:

1. Fetch real-time Bitcoin price data using CoinGecko API
2. Process data using Apache Ray for distributed computing
3. Perform time-series analysis with moving averages
4. Generate interactive visualizations

There are two primary entry points:

- **`bitcoin_API.ipynb`** — Interactive API exploration and documentation
- **`bitcoin_example.ipynb`** — End-to-end pipeline demonstration

For detailed API documentation, refer to `bitcoin_API.md`.

---

## 2. Project Files

```text
bitcoin_utils.py               # shared utilities for data processing and analysis
bitcoin_API.ipynb             # interactive API walkthrough
bitcoin_API.md               # API documentation
bitcoin_example.ipynb        # example pipeline implementation
bitcoin_example.md          # pipeline documentation
bitcoin_7d_plus_realtime.csv # historical Bitcoin price data

architecture.png            # system architecture diagram
bitcoin_flowchart.png      # process flow visualization
price_moving_avg_runtime.png # performance metrics visualization

Dockerfile            # container specification
docker_build.sh      # build container
docker_bash.sh       # start interactive shell
docker_jupyter.sh    # launch JupyterLab
docker_exec.sh       # execute commands
docker_push.sh       # push to registry
docker_clean.sh      # cleanup
docker_name.sh       # naming helper

requirements.txt      # Python dependencies
install_jupyter_extensions.sh  # Jupyter setup
install_project_packages.sh    # Project dependencies
bashrc               # Shell configuration

```

---

## 3. Prerequisites & Setup

1. **Clone the repo & navigate**
   ```bash
   git clone https://github.com/[username]/tutorials.git
   cd tutorials/DATA605/Spring2025/projects/TutorTask93_Spring2025_Real-Time_Bitcoin_Data_Processing_with_Apache_Ray
   ```

2. **Install Dependencies**
   - Python 3.8+
   - Required packages:
     - ray==2.10.0
     - pandas
     - requests
     - plotly
     - yfinance
     - scikit-learn
     - statsmodels
     - jupyterlab
     - matplotlib
     - tensorflow

3. **Docker Setup**
   - Install Docker (Desktop/Engine)
   - Build the container:
     ```bash
     chmod +x docker_*.sh
     ./docker_build.sh
     ```

---

## 4. Build & Run Docker

1. **Build the image**
   ```bash
   ./docker_build.sh (If you use ubuntu add "sudo" when you run docker commands, for eg: "sudo ./docker_build.sh")
   ```

2. **Start JupyterLab**
   ```bash
   ./docker_jupyter.sh
   ```
   - Access by copy pasting one of the links generated

3. **Interactive Shell**
   ```bash
   ./docker_bash.sh
   ```

---

## 5. Usage

### 5.1 API Exploration
Open `bitcoin_API.ipynb` in JupyterLab to:
- Learn about available API endpoints
- Test data fetching
- Explore real-time processing

### 5.2 Run Example Pipeline
Open `bitcoin_example.ipynb` to see:
- Complete data pipeline
- Analysis examples
- Visualization demos

---

## 6. Features

1. **Real-time Data Processing**
   - Live Bitcoin price fetching
   - Distributed processing with Ray
   - Automated data collection

2. **Analysis Capabilities**
   - Moving averages calculation
   - Basic statistics
   - Time series analysis

3. **Visualization**
   - Interactive price charts
   - Moving average plots
   - Performance metrics

---



## 7. References

- [Ray Documentation](https://docs.ray.io/)
- [CoinGecko API Docs](https://www.coingecko.com/en/api/documentation)
- [JupyterLab Documentation](https://jupyterlab.readthedocs.io/)