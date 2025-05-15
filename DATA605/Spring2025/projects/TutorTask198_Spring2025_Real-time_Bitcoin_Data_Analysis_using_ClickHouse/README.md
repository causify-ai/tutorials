# TutorTask198_Spring2025_Real-time_Bitcoin_Data_Analysis_using_ClickHouse

# 📈 Real-time Bitcoin Data Analysis using ClickHouse

**Why ClickHouse?**
We use ClickHouse for its high-performance columnar storage engine, vectorized query execution, data compression, and real-time OLAP capabilities, making it ideal for low-latency analytics and high ingestion rates on large-scale Bitcoin time-series data.

A real-time data analytics pipeline for Bitcoin price tracking, built with Python, Docker, ClickHouse, and Streamlit. This project demonstrates ingestion, storage, time series analysis, and visualization of cryptocurrency price data.

---

## 🧠 Project Overview

This project sets up a **real-time analytics system** that:
- Ingests **hourly Bitcoin prices** from the [CoinGecko API](https://www.coingecko.com/en/api).
- Stores the data in a high-performance **ClickHouse** database.
- Performs **time series analytics** such as moving averages, volatility, anomaly detection, and forecasting.
- Visualizes insights in an interactive **Streamlit dashboard** and optional **Flask-based dashboards**.

---

## 🏗️ Tech Stack

| Component       | Technology     |
|----------------|----------------|
| Database        | ClickHouse (port **8123**) |
| Ingestion       | Python (requests, pandas) |
| Analysis        | statsmodels, Prophet, scikit-learn |
| Visualization   | Streamlit, Plotly, Matplotlib |
| Orchestration   | Docker + Docker Compose |
| Optional        | Flask for dashboard export |

---

## 📦 Directory Structure

```
.
├── ingest/                         # Data ingestion modules
├── analysis/                       # Time series analytics
├── visualization/                  # Dashboards and plotting
├── pipeline/                       # Schema setup, pipeline runner
├── config/                         # DB clients, schema
├── docker-compose.yml              # Docker orchestration
├── Dockerfile                      # App container
├── requirements.txt                # Python dependencies
├── streamlit_app.py                # Main Streamlit UI
├── main.py                         # Optional Flask server + dashboard
├── bitcoin_clickhouse_demo.ipynb   # Jupyter notebook: setup, ingestion, querying, analysis, forecasting & visualization
└── start.sh                        # Unified startup script
```

---

## 🚀 Getting Started

### 🐳 Option 1: Run via Docker (Recommended)

```bash
# 1. Build and start all components
docker compose up --build -d

# 2. Streamlit dashboard
http://localhost:8501

# 3. Optional: Flask dashboard (static HTML export)
http://localhost:5001

# 4. ClickHouse Web UI (port 8123)
http://localhost:8123
```

---

### 🍎 Option 2: Run Locally on macOS (No Docker)

> First, install ClickHouse via Homebrew

> Then in a new terminal tab, run the following (inside project folder):

```bash
# Create the schema
python setup_clickhouse.py

# Option A: Use the provided startup script
./start.sh
```

> Or manually run services in parallel:

```bash
# Start app logic (Flask + Plotly dashboard builder)
python3 main.py &

# Start Streamlit dashboard
streamlit run streamlit_app.py \
  --server.port=8501 \
  --server.address=0.0.0.0 &
```

---

## 🧪 Features & Functionality

### ✅ Data Ingestion
- Historical BTC price (365 days)
- Real-time hourly data
- Duplicate-safe inserts
- Resilient retry logic

### 📈 Time Series Analysis
- Moving Averages
- Rolling Volatility
- Daily Returns
- Bollinger Bands
- Anomaly Detection (±2σ)
- Forecasting with [Prophet](https://facebook.github.io/prophet/)

### 📊 Visualizations
- Streamlit-based interactive dashboard
- Plotly forecasts with confidence intervals
- Flask-based static dashboard HTMLs (optional)

---

## 📊 Live Dashboard Preview

Once running, explore metrics like:

- 💰 Latest Price
- 📉 Rolling Averages
- 🚨 Anomalies
- 🔮 Forecast Trends
- 📉 Bollinger Bands
- 🔁 Daily Returns

---

## 🔄 Background Tasks

| Task | Interval |
|------|----------|
| 🕐 Auto-ingestion (live BTC) | Every 60 mins |
| 📈 Dashboard refresh (HTML)  | Every 60 secs |

---

## 🔧 Developer Tools

| Tool         | URL or Usage         |
|--------------|----------------------|
| Streamlit    | http://localhost:8501 |
| Flask app    | http://localhost:5001 |
| ClickHouse UI| http://localhost:8123 |
| Jupyter      | `docker exec -it bitcoin-app bash` → `jupyter notebook` |

- Jupyter Notebook ▶️ Open `bitcoin_clickhouse_demo.ipynb` for the full end-to-end demo


---

## 📚 References

- [ClickHouse Docs](https://clickhouse.com/docs/en/)
- [ClickHouse SQL Reference](https://clickhouse.com/docs/en/sql-reference/)
- [CoinGecko API](https://www.coingecko.com/en/api)
- [Prophet Forecasting](https://facebook.github.io/prophet/)
- [Streamlit](https://docs.streamlit.io/)

---

## 📝 License

MIT License © 2025 Vishwaksena Vishnu Simha Dingari

---

<!-- ## Running Locally

To start the application locally, use:

```bash
./start.sh
```

## Running with Docker

To build and run the application in Docker using Docker Compose, use:

```bash
docker compose up --build -d
```

The running project implementation and usage of some functions are in `template.ipynb`.


# Tutorial Template: Two Docker Approaches

- This directory provides two versions of the same tutorial setup to help you
  work with Jupyter notebooks and Python scripts inside Docker environments

- Both versions run the same code but use different Docker approaches, with
  different level of complexity and maintainability

## 1. `data605_style` (Simple Docker Environment)

- This version is modeled after the setup used in DATA605 tutorials
- This template provides a ready-to-run environment, including scripts to build,
  run, and clean the Docker container.

- For your specific project, you should:
  - Modify the Dockerfile to add project-specific dependencies
  - Update bash/scripts accordingly
  - Expose additional ports if your project requires them

- build the image
    - `docker build -t my-multi-process-app .`

- run it, publishing both ports
    - `docker run -d -p 8501:8501 -p 8888:8888 -p 5001:5000 --name my-app-container my-multi-process-app`


## 2. `causify_style` (Causify AI dev-system)

- This setup reflects the approach commonly used in Causify AI dev-system
- **Recommended** for students familiar with Docker or those wishing to explore a
  production-like setup
- Pros
  - Docker layer written in Python to make it easy to extend and test
  - Less redundant since code is factored out
  - Used for real-world development, production workflows
  - Used for all internships, RA / TA, full-time at UMD DATA605 / MSML610 /
    Causify 
- Cons
  - It is more complex to use and configure
  - More dependencies from the 
- For thin environment setup instructions, refer to:  
  [How to Set Up Development on Laptop](https://github.com/causify-ai/helpers/blob/master/docs/onboarding/intern.set_up_development_on_laptop.how_to_guide.md)

## Reference Tutorials

- The `tutorial_github` example has been implemented in both environments for you
  to refer to:
  - `tutorial_github_data605_style` uses the simpler DATA605 approach
  - `tutorial_github_causify_style` uses the more complex Causify approach

- Choose the approach that best fits your comfort level and project needs. Both
  are valid depending on your use case. -->
