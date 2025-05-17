# Real-Time Bitcoin Price Analysis using SHAP

**Author**: Swattik Maiti 
**Date**: 2025-05-16  
**Course**: DATA605 — Spring 2025

---


## Table of Contents

- [1. Project Overview](#1-project-overview)
- [2. Project Files](#2-project-files)
- [3. Prerequisites & Setup](#3-prerequisites--setup)
- [4. Docker Build & Execution](#4-docker-build--execution)
- [5. Usage](#5-usage)
  - [5.1 Run the API functionality demo](#51-run-the-api-functionality-demo)
  - [5.2 Run the full pipeline](#52-run-the-full-pipeline)
  - [5.3 Explore interactively via notebooks](#53-explore-interactively-via-notebooks)
- [6. Troubleshooting](#6-troubleshooting)
- [7. References](#7-references)

---

## 1. Project Overview

This project builds a modular Python pipeline to:

1. Fetch **real-time Bitcoin price, volume, and market cap data** from the CoinGecko API  
2. Perform **exploratory data analysis** and **stationarity checks**  
3. Create engineered time-series features including lags and rolling statistics  
4. Train an **XGBoost regression model** to predict the next-hour Bitcoin price  
5. Use **SHAP (SHapley Additive Explanations)** to explain model predictions both globally and locally  

There are two primary entry points:

- `SHAP.API.ipynb`: A **tutorial notebook** demonstrating SHAP's Python API and visualizations  
- `SHAP.example.ipynb` / `SHAP.example.py`: The **end-to-end pipeline**, implemented both as a notebook and script

---

## 2. Project Files

```text
SHAP.API.ipynb           # Minimal tutorial covering SHAP API usage
SHAP.API.md              # Companion markdown documentation for SHAP API

SHAP.example.ipynb       # End-to-end pipeline: data → train → predict → explain
SHAP.example.py          # Script version of the pipeline
SHAP.example.md          # Markdown summary of the pipeline notebook

config/
  └─ config.yaml         # Runtime config for API calls (CoinGecko URL, currency, days)

data/
  └─ (generated runtime) # Temporary market data fetched via API

src/
  ├─ ingestion/
  │   └─ fetch_data.py               # Real-time data wrappers for CoinGecko API
  ├─ preprocessing/
  │   ├─ eda_hourly_data.py         # EDA functions for time-series visualization
  │   └─ stationarity_checks.py     # Rolling stats + Augmented Dickey-Fuller test
  ├─ features/
  │   └─ feature_engineering.py     # Lag & rolling feature creation module
  ├─ shap_utils/
  │   └─ shap_analysis.py           # Encapsulated SHAP visualizations in a class wrapper

docker_data605_style/
  ├─ Dockerfile                     # Base image with Jupyter + Python 3
  ├─ docker_build.sh                # Builds the container
  ├─ docker_jupyter.sh              # Launches Jupyter notebook server
  ├─ docker_bash.sh                 # Opens an interactive bash shell
  ├─ install_project_packages.sh    # Installs pip dependencies inside container
  └─ bashrc, etc_sudoers, utils.sh  # Additional helper configs

requirements.txt         # Python dependencies
.env                     # (optional) to store API keys if using a paid tier
```

---


## 3. Prerequisites & Setup

1. **Clone the project:**
   ```bash
   git clone https://github.com/causify-ai/tutorials.git
   cd tutorials/DATA605/Spring2025/projects/TutorTask216_Spring2025_Analyzing_Bitcoin_Price_Data_Streams_using_SHAP
   ```
2. **Install Docker Desktop for your OS.**
3. **(Optional)** Create a `.env` file for your API key:
```ini
COINGECKO_API_KEY=your_key_here
``` 

---

## 4. Docker Build & Execution (data605_style)

**Note**: I copied `install_jupyter_extensions.sh` and `.bashrc` from the `docker_common` directory into my local project folder. I also made slight modifications to the Docker-related scripts (`docker_bash.sh`, `docker_build.sh`, `docker_jupyter.sh`) and the `Dockerfile` based on my project requirements.



2. **Build the Docker image**

   ```bash
   chmod +x docker_data605_style/docker_*.sh
   ./docker_data605_style/docker_build.sh
   ```

3. **Option A: Interactive Bash Shell**

   * **Step 1:** Start the container.

     ```bash
     ./docker_data605_style/docker_bash.sh
     ```

   * **Step 2:** Inside the container (e.g., `root@<id>:/data#`), navigate to the project folder if not already there:

     ```bash
     cd /data
     ```

   * **Step 3:** Install dependencies and launch Jupyter Notebook:

     ```bash
     pip install -r requirements.txt
     jupyter notebook --no-browser --ip=0.0.0.0 --port=8888 --allow-root
     ```

   * **Step 4:** Access the notebook:

     - Copy and paste the full tokenized link from the terminal into your browser.
     - If you land on an authentication page, try visiting:  
       `http://localhost:8888/lab?token=...`  

   * **(Optional)** Run the pipeline script directly:

     ```bash
     python3 SHAP.example.py
     ```

4. **Option B: Direct JupyterLab**

   * **Step 1:** Launch Jupyter in one go:

     ```bash
     ./docker_data605_style/docker_jupyter.sh
     ```
   * **Step 2:** In a second terminal (or the same session), install deps:

     ```bash
     pip install -r /data/requirements.txt
     ```
   * Visit `http://localhost:8888/lab?token=…` in your browser.

---

## 5. Usage

### 5.1 Run the API functionality demo

```bash
jupyter notebook SHAP.API.ipynb
```

This notebook demonstrates:

- `TreeExplainer`, `DeepExplainer`, and `KernelExplainer`
- SHAP visualizations: summary, force, waterfall, decision, dependence

---

### 5.2 Run the full pipeline

As a script:

```bash
python SHAP.example.py
```

As a notebook:

```bash
jupyter notebook SHAP.example.ipynb
```

This pipeline will:

- Fetch real-time hourly Bitcoin data
- Engineer features (lags, rolling stats)
- Train an XGBoost regressor
- Evaluate predictions
- Interpret using SHAP

---
### 5.3 Explore interactively via notebooks

Recommended order:

1. `SHAP.API.ipynb` — learn SHAP API
2. `SHAP.example.ipynb` — full use-case pipeline

Click **“Restart & Run All”** in JupyterLab for best results.

---


## 6. Usage

### 6.1 Run the API demo script  
```bash
python databricks_cli.API.py
```  
This will:

- Create a cluster  
- Check status  
- Upload/download a test file  
- Submit and poll a job run  
- Delete the cluster  

### 6.2 Run the full pipeline script  
```bash
python databricks_cli.example.py
```  
This executes the entire fetch→forecast→plot flow and writes visuals to `output_plots/`.

### 6.3 Interactive Notebooks  
Open in JupyterLab and **Restart & Run All**:

- `databricks_cli.API.ipynb`  
- `databricks_cli.example.ipynb`

---

## 6. Troubleshooting

- **403 Forbidden from API?** — CoinGecko API key may be rate-limited or missing  
- **SHAP rendering issues?** — Use `%matplotlib inline` and update `shap`, `ipython`, `traitlets`  
- **Docker port not accessible?** — Ensure you used `-p 8888:8888` when launching the container  
- **"Token authentication required"** — Use the full link printed by `jupyter notebook`, including `?token=...`

---

## 7. References

- [SHAP GitHub](https://github.com/shap/shap)  
- [CoinGecko API Docs](https://www.coingecko.com/en/api/documentation)  
- [XGBoost Docs](https://xgboost.readthedocs.io/en/stable/index.html)  
- [Augmented Dickey-Fuller Test (Statsmodels)](https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.adfuller.html)

---