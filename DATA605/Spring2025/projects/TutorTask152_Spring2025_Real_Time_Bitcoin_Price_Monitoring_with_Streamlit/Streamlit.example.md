# Streamlit.example.md

## Table of Contents
- [1. Project Purpose](#1-project-purpose)
- [2. Repository Contents](#2-repository-contents)
- [3. Core Workflow](#3-core-workflow)
- [4. Detailed File Breakdown](#4-detailed-file-breakdown)
  - [4.1 `Streamlit.example.py`](#41-streamlitexamplepy)
  - [4.2 `Streamlit.example.ipynb`](#42-streamlitexampleipynb)
- [5. Running the Dashboard Locally or using Docker](#5-running-the-dashboard-locally)
  - [Configure CryptoPanic API Key](#configure-cryptopanic-api-key)
- [6. Extending the Project](#6-extending-the-project)
- [7. References & Further Reading](#7-references--further-reading)


## 1. Project Purpose

**Real-Time Bitcoin Price Monitoring with Streamlit** demonstrates how to turn a pure-Python data-science workflow into a polished, interactive web dashboard—no HTML, CSS, or JavaScript required.
The solution ingests live market data from the CoinGecko REST API, enriches it with technical-analysis metrics, and exposes the results through a one-click Streamlit interface.

---

## 2. Repository Contents

| File | Role | When to Use |
|------|------|-------------|
| **`Streamlit.example.py`** | Production-ready Streamlit app. Run it with `streamlit run Streamlit.example.py` to launch the full dashboard. | For live demos and user interaction. |
| **`Streamlit.example.ipynb`** | Jupyter notebook that mirrors the core data pipeline step-by-step, complete with narrative explanations, plots, and code snippets. | For exploratory analysis, reproducibility, and teaching. |
| **`Streamlit_utils.py`** <sup>(imported)</sup> | Utility layer that wraps CoinGecko endpoints (`get_current_price`, `get_historical_data`, …) and computes TA indicators. | Shared across both the notebook and the Streamlit app. |

> **Why two entry points?**
> The notebook is ideal for iterative exploration and academic submission, while the `.py` script packages the exact same logic behind a real-time, shareable dashboard.

---

## 3. Core Workflow

1. **User Input** *(sidebar)*
   * Select coin (`BTC`, `ETH`, `ADA`, …)
   * Pick date range (7–365 days)
   * Choose moving-average window and anomaly sensitivity
   * Optional: forecast horizon
2. **Data Layer**
   * `requests` pulls **live** and **historical** price data from CoinGecko.
   * `@st.cache_data(ttl=300)` caches results to avoid rate-limit issues while keeping data fresh.
3. **Processing Layer**
   * **Moving Average**, **RSI**, **MACD**, **Bollinger Bands** via *pandas* and *ta-lib* wrappers.
   * **Z-score anomaly detection** flags outliers in day-to-day returns.
   * **Prophet forecasting** produces probabilistic price projections.
4. **Visual Layer**
   * Plotly charts rendered directly inside Streamlit with `st.plotly_chart`.
   * KPI tiles (`st.metric`) and collapsible news feed (`st.expander`).
5. **Optional Portfolio Tracker**
   * Uses `st.session_state` to remember coin holdings across reruns and compute current valuation.

![Architecture](https://raw.githubusercontent.com/streamlit/brand-assets/main/streamlit-mark.png)

---

## 4. Detailed File Breakdown

### 4.1 `Streamlit.example.py`

| Section | Key Streamlit APIs | Description |
|---------|-------------------|-------------|
| **Page Config** | `st.set_page_config` | Sets title, wide layout, and expanded sidebar. |
| **Sidebar** | `st.selectbox`, `st.slider`, `st.number_input` | Collects user-defined parameters. |
| **Caching** | `@st.cache_data` | Memoises API calls (`get_current_price`, `get_historical_data`) for 5 min. |
| **KPIs** | `st.metric` | Displays live USD price. |
| **Charts** | `st.plotly_chart` | Price + MA, TA overlays, RSI, MACD, Bollinger Bands, forecast curves. |
| **Anomalies** | Plotly scatter markers | Red dots above/below bands when Z-score > threshold. |
| **Forecast** | Prophet, `st.button`, `st.spinner` | Trains model on demand and visualises forecast & components. |
| **News** | `st.expander` | Shows latest CryptoPanic headlines. |
| **Portfolio** | `st.session_state`, `st.number_input`, `st.metric` | Lets user track holdings value in real time. |

### 4.2 `Streamlit.example.ipynb`

The notebook reproduces every processing step without the Streamlit UI, adding rich Markdown explanations:

1. **Setup & Imports** – loads helper functions from `Streamlit_utils.py`.
2. **Fetching Data** – demonstrates API calls and inspects raw JSON.
3. **Analysis** – calculates MAs and technical indicators, prints sample tables.
4. **Anomaly Detection** – shows filtered DataFrame where `anomaly == True`.
5. **Forecasting** – fits Prophet and plots forecast vs. actual.
6. **Visualisation** – embeds Plotly graphs inline for quick inspection.

This makes the analytical logic easy to grade or extend in an academic context.

---

## 5. Running the Dashboard Locally or using Docker

### 5.1 Running Locally
```bash
# 1. Install dependencies
pip install -r requirements.txt
```

### Configure CryptoPanic API Key

This dashboard uses the CryptoPanic API to fetch the latest news headlines. To avoid exposing your API key in the repository, configure it via an environment variable or a `.env` file:

- **Environment variable**
  ```bash
  export CRYPTOPANIC_API_KEY=your_api_key_here
  ```
- **.env file**
  1. Create a file named `.env` in the project root with the following content:
     ```dotenv
     CRYPTOPANIC_API_KEY=your_api_key_here
     ```
  2. Ensure `.env` is listed in your `.gitignore` so it isn’t committed to version control.

The app will load the key in Python using:
```python
import os
api_key = os.getenv("CRYPTOPANIC_API_KEY")
```

```bash
# 2. Launch the app
streamlit run Streamlit.example.py
```

Streamlit will open `http://localhost:8501` in your browser. Any code change auto-reloads.

---

### 5.2 Using Docker

### Configure CryptoPanic API Key
Refer the above block

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

## 6. Extending the Project

* **Additional Coins:** Add symbols to `CRYPTO_LIST` and voilà.
* **Indicators:** Plug in any *ta*-lib function, or custom metrics.
* **Alerting:** Combine anomaly detection with `st.toast` or email notifications.
* **Deployment:** Host on **Streamlit Community Cloud** (free tier) or Dockerise for any cloud provider.

---

## 7. References & Further Reading

* **Streamlit Docs** – <https://docs.streamlit.io>
* **CoinGecko API** – <https://www.coingecko.com/en/api/documentation>
* **CryptoPanic API** – <https://cryptopanic.com/developers>
* **Prophet** – <https://facebook.github.io/prophet/>
* **Statsmodels** – <https://www.statsmodels.org/>

---

*Last updated: 12 May 2025*
