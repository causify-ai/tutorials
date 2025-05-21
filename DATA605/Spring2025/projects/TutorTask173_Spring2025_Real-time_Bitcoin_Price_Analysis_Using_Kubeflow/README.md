
# Real-Time Bitcoin Price Analysis with Kubeflow and Docker

**In this PR, I've resolved the Gitleak Issue**

**Name**: Anto Delin Xavier  
**UID** : 121287793
**Course**: DATA605
**Project**: Real-Time_Bitcoin_Price_Analysis_Using_Kubeflow

---

## 1. Project Overview

This project sets up an end-to-end pipeline that:

- Fetches real-time Bitcoin prices from the CoinGecko API
- Stores the data in a PostgreSQL-compatible TimescaleDB instance
- Visualizes the results in real time via local scripts
- Integrates with **Kubeflow Pipelines** to automate recurring fetch jobs in a Kubernetes cluster

Key components:
- Live price fetching using the **CoinGecko API**
- Scheduled execution through **Kubeflow Pipelines**
- Containerization with **Docker**
- Data visualization and forecasting using **Python**


---

## 2. Folder Structure

```
TutorTask173_Spring2025_Real-time_Bitcoin_Price_Analysis_Using_Kubeflow/
│   
│
├── markdowns/               
│   ├── bitcoin.API.md  # documentation of API usage
│   └── bitcoin.example.md  # documentation for example
│
├── scripts and docker fetcher/                 
│   ├── fetch_bitcoin_price.py     # main fetch script used by container
│   ├── bitcoin_pipeline.py        # pipeline definition for Kubeflow
│   ├── compile_pipeline.py        # compiles to YAML pipeline
│   ├── bitcoin_utils.py           # helper functions
│   ├── Dockerfile                 # Docker image spec
│   ├── bitcoin_pipeline.yaml      # generated yaml file to upload to Kubeflow UI
├   ├── Bitcoin_TimeSeriesAnalaysis.ipynb # Timeseries analysis on real time fetched data and historical data
│   └── bitcoin_price_log_from_db.csv # Bitcoin live entries
│   
│── bitcoin.example.ipynb     
│── bitcoin.API.ipynb   # documentation of API usage          
└── README.md



```

---

There are **two main execution**:
- **Docker Compose Setup**: Uses Docker for development/testing
- **Kubeflow Pipelines Deployment**: Runs automated jobs in a Kubernetes cluster

## 3. Docker-Based Setup

### 3.1 Requirements

- Docker Desktop
- DockerHub login (for image upload)

### 3.2 Build and Run


1. **Build and run** using Docker Compose:
```bash
docker-compose up --build
```

2. This will:
   - Run the fetcher container once

This will fetch the live bitcoin data and store as csv for timeseries analysis
---

## 4. Kubeflow Pipelines Setup


### Step 1: Compile Pipeline

```bash
python compile_pipeline.py
```

Generates `bitcoin_pipeline.yaml`.

### Step 2: Upload to Kubeflow UI

- Open your Kubeflow dashboard
- Upload the compiled `bitcoin_pipeline.yaml`
- Create a recurring run (e.g., every 1 minute)

### Step 3: Deploy  Kubernetes

```bash
kubectl get pods -n kubeflow
```

---

## 5. Visualize and Analyze Data

fetch  data from the bitcoin_price_log_from_db.csv


 run the Jupyter notebook:

```bash
jupyter notebook Bitcoin_TimeSeriesAnalaysis.ipynb 
```
(make sure to have generated bitcoin_price_log_from_db.csv in the same folder)

This generates:
- Time series analysis on the fetched data

---

## 6. Scripts

### bitcoin_utils.py

- Contains the `BitcoinPriceFetcher` class and connection utilities

### fetch_bitcoin_price.py

- The primary script to fetch and log price data

### bitcoin_pipeline.py / compile_pipeline.py

- Constructs a Kubeflow-compatible pipeline using the KFP SDK

### Bitcoin_TimeSeriesAnalaysis.ipynb

- Do the Time Series Analysis with feched live data (taken from csv)

---

## 9. References

- [Kubeflow Pipelines](https://www.kubeflow.org/docs/components/pipelines/)
- [CoinGecko API](https://www.coingecko.com/en/api)
- [Docker Compose Docs](https://docs.docker.com/compose/)
