# Real-Time Bitcoin Price Monitoring with Streamlit

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Repository Structure](#repository-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Set Up a Virtual Environment (Recommended)](#2-set-up-a-virtual-environment-recommended)
  - [3. Install Python Dependencies](#3-install-python-dependencies)
- [Running the App Locally](#running-the-app-locally)
- [Docker Deployment](#docker-deployment)
  - [Quickstart with Scripts](#quickstart-with-scripts)
  - [Manual Docker Commands](#manual-docker-commands)
- [Configuration](#configuration)
- [Jupyter Notebooks](#jupyter-notebooks)
- [Contributing](#contributing)

## Overview

This project demonstrates how to transform a pure-Python data-science workflow into a polished, interactive web dashboard using Streamlit—without writing any HTML, CSS, or JavaScript. It ingests live and historical cryptocurrency data from the CoinGecko REST API, enriches it with technical-analysis metrics, detects anomalies, and provides probabilistic forecasts via Prophet. You can run it locally, in a Docker container, or explore the analysis step-by-step in the provided Jupyter notebooks.

Author: Manan J. Ambaliya
UID: 121118776
Email: manan001@umd.edu

## Features

- **Live Price Monitoring**: Fetch real-time cryptocurrency prices (e.g., BTC, ETH, ADA).
- **Historical Data Analysis**: Retrieve and visualize up to 365 days of price history.
- **Technical Indicators**: Compute Moving Averages, RSI, MACD, Bollinger Bands, and more via `ta`-lib wrappers.
- **Anomaly Detection**: Highlight outliers in daily returns using Z-score methods.
- **Forecasting**: Generate probabilistic price projections with Facebook Prophet.
- **Portfolio Tracking**: (Optional) Maintain coin holdings across sessions and compute current valuations.
- **Dockerized Deployment**: One-click container build and run via helper scripts.
- **Modular Codebase**: Shared utility layer in `Streamlit_utils.py` for clean, reusable functions.

## Repository Structure

```
├── Dockerfile                     # Container specification
├── docker_build.sh                # Build Docker image
├── docker_run.sh                  # Launch Docker container
├── docker_bash.sh                 # Open a shell inside the container
├── docker_clean.sh                # Remove containers and images
├── requirements.txt               # Python dependencies
├── Streamlit_utils.py             # API wrapper & utility functions
├── Streamlit.example.py           # Production-ready Streamlit app entry point
├── Streamlit.example.ipynb        # Notebook version of the Streamlit pipeline
├── Streamlit.example.md           # Documentation for the example app
├── Streamlit.API.ipynb            # Notebook demonstrating the raw API wrapper
├── Streamlit.API.md               # Documentation for the API notebook
└── README.md                      # (This file)
```

## Prerequisites

- **Python**: Version 3.10 or higher
- **pip**: Package installer for Python
- **Git**: To clone the repository
- **Docker** (optional): For containerized deployment

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

### 2. Set Up a Virtual Environment (Recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate   # macOS/Linux
.\.venv\Scripts\activate  # Windows
```

### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Running the App Locally

```bash
streamlit run Streamlit.example.py --server.port=8501
```

Then open your browser at [http://localhost:8501](http://localhost:8501).

## Docker Deployment

This project provides helper scripts to simplify Docker workflows:

| Script            | Purpose                                    |
|-------------------|--------------------------------------------|
| `docker_build.sh` | Build the Docker image                     |
| `docker_run.sh`   | Launch a container and expose port 8501    |
| `docker_bash.sh`  | Open an interactive shell inside the container |
| `docker_clean.sh` | Stop and remove containers/images          |
| `docker_dev.sh`   | All in one, First Clear the previous image then Build the image then launch the container     |


### Quickstart with Scripts

```bash
# Make all scripts executable
chmod +x docker_*.sh

# Build the image
./docker_build.sh

# Run the container
./docker_run.sh

# (Optional) Get a shell inside the container
./docker_bash.sh

# (Optional) Clean up containers and images
./docker_clean.sh

# (Optional) Clean up, Build, and Run
./docker_dev.sh
```

### Manual Docker Commands

If you prefer manual steps:

```bash
# Build the image
docker build -t streamlit-bitcoin-tracker .

# Run the container
docker run -d -p 8501:8501 --name streamlit-bitcoin-tracker streamlit-bitcoin-tracker

# (Optional) Access a container shell
docker exec -it streamlit-bitcoin-tracker /bin/bash

# (Optional) Stop and remove container & image
docker stop streamlit-bitcoin-tracker
docker rm streamlit-bitcoin-tracker
docker rmi streamlit-bitcoin-tracker
```

## Configuration

- **Sidebar Controls** in `Streamlit.example.py` allow you to select:
  - Cryptocurrency symbol (e.g., `BTC`, `ETH`, `ADA`)
  - Date range (7–365 days)
  - Moving average window
  - Anomaly detection threshold
  - Forecast horizon
- To support additional coins, edit the `CRYPTO_LIST` constant in `Streamlit_utils.py` or directly in `Streamlit.example.py`.

## Jupyter Notebooks

- **Streamlit.example.ipynb**: Mirrors the production pipeline step-by-step with inline narrative, tables, and plots—ideal for teaching or exploration.
- **Streamlit.API.ipynb**: Demonstrates usage of the raw CoinGecko API via `Streamlit_utils.py` for custom analytics tasks.
- Documentation for each notebook is available in `Streamlit.example.md` and `Streamlit.API.md`, respectively.

## Contributing

Contributions, issues, and feature requests are welcome! Please:

1. Fork the repository
2. Create a new branch (`git checkout -b feature-name`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature-name`)
5. Open a Pull Request

---

*Last updated: May 12, 2025*
