
#  Real-Time Bitcoin Price Forecasting with PyCaret




### **Project Overview**  


This project implements an end-to-end automated machine learning pipeline for real-time Bitcoin price forecasting using PyCaret, an open-source low-code machine learning library. The system connects to cryptocurrency APIs (CoinGecko/CoinMarketCap) to fetch live Bitcoin price data at regular intervals, processes the data using pandas, and leverages PyCaret’s specialized time series module to train, compare, and deploy forecasting models. The goal is to demonstrate how PyCaret’s automated ML capabilities can simplify complex time series analysis tasks while maintaining robustness in volatile market conditions.  

The workflow begins with real-time data ingestion, where Python’s `requests` library fetches OHLC (Open-High-Low-Close) price data and trading volume from cryptocurrency APIs. This data undergoes preprocessing to handle missing values, normalize timestamps, and engineer relevant features like moving averages and relative strength index (RSI). PyCaret then automates the entire model development lifecycle—splitting the data into training and validation sets (using time-series-specific cross-validation), testing multiple algorithms, and selecting the best-performing model based on metrics like RMSE (Root Mean Squared Error) and MAE (Mean Absolute Error). The selected model generates price predictions for future time horizons with confidence intervals, which are visualized interactively using Plotly.  

A key innovation of this project is its Dockerized environment, which ensures reproducibility across systems. The container includes all dependencies (PyCaret, pandas, Plotly) and scripts to fetch data, run forecasts, and update visualizations automatically. This setup is particularly valuable for financial analysis, where model performance can degrade rapidly due to market volatility, requiring frequent retraining. By combining PyCaret’s low-code efficiency with real-time data pipelines, the project offers a template for rapid prototyping of time series models in finance.  


### 1. **PyCaret API Exploration (`pycaret.API.ipynb`)**  

  -  **Setup Validation**: PyCaret time series experiment initialized with `fh=24` (24-hour forecast horizon) and no errors in data loading.  
  -  **Model Comparison**: At least 3 models (e.g., ARIMA, Prophet, Exponential Smoothing) compared with RMSE < 500 USD (benchmark for Bitcoin’s volatility).  


### 2. **Bitcoin Forecasting Example (`bitcoin.example.ipynb`)**  
 
  -  **Data Ingestion**: Real-time data fetched from CoinGecko API with:  
    - Columns: `timestamp`, `price`, `volume` (no missing values).  
    - Updated every 1 hour (cron job logic in `bitcoin_utils.py`).  
  -  **Visualization**: Interactive Plotly chart showing:  
    - Historical prices (30-day window).  
    - Predicted values with confidence interval (e.g., `plotly.express.line`).  
  -  **Deployment**: Docker container runs end-to-end without errors (`docker_jupyter.sh` launches notebook).  
## Technical Implementation


##### 1: Repository Setup
```bash
git clone --recursive git@github.com:causify-ai/tutorials.git
cd tutorials

# Verify remote
git remote -v
```
** Expected Output:**
```
origin  git@github.com:causify-ai/tutorials.git (fetch)
origin  git@github.com:causify-ai/tutorials.git (push)
```

### : Commands used to create a branch
```bash
git checkout master
git pull origin master
git checkout -b TutorTask283_Spring2025_Real-Time_Bitcoin_Data_Analysis_with_PyCaret
```
** Expected Output:**
```
Switched to a new branch 'TutorTask283_Spring2025_Real-Time_Bitcoin_Data_Analysis_with_PyCaret'
```


##  Docker Setup 

### Commands used for building the Image
```bash
docker build -t bitcoin .
git add Dockerfile
git commit -m "build: Dockerfile for bitcoin analysis image"
```

### Command to run the Container
```bash
docker run -d \
  -p 8888:8888 \
  -v "$PWD":/home/jovyan/work \
  --name bitcoin_analysis \
  bitcoin
```
**Verify container:**
```bash
docker ps --filter "name=bitcoin_analysis"
```
** Expected Output:**
```
CONTAINER ID   IMAGE    ...   NAMES
a1b2c3d4e5f6   bitcoin  ...   bitcoin_analysis
```

---


### PyCaret Workflow


##### 1. Initialize experiment


##### 2. Compare models (15+ algorithms tested)


##### 3. Create final model


##### 4. Save pipeline



### Typical Git Commands During Development:
```bash
# After making changes
git status
git diff

# Stage changes
git add bitcoin_utils.py pycaret.API.ipynb

# Commit with message
git commit -m "feat: implemented data fetching and preprocessing"

# Push to remote
git push origin TutorTask283_Spring2025_Real-Time_Bitcoin_Data_Analysis_with_PyCaret
```
** Expected Push Output:**
```
Enumerating objects: 7, done.
...
To github.com:causify-ai/tutorials.git
 * [new branch] TutorTask283... -> TutorTask283...
```

---

## 🔀 Pull Request Process

### 1. Create PR from GitHub UI
- Compare: `TutorTask283...` → Base: `master`
- Title: `TutorTask283: PyCaret Bitcoin Time Series Analysis`
- Description:
  
  ## Changes
  - Implemented real-time BTC data pipeline
  - Dockerized PyCaret environment
  - Added forecasting notebooks
  
  ## Verification Steps
  1. Build image: `docker build -t bitcoin .`
  2. Run container: `docker run --name bitcoin_analysis ...`
  

### 2. Update PR Iteratively
```bash
# Make new changes
git add .
git commit -m "docs: added expected outputs section"
git push origin TutorTask283_Spring2025_Real-Time_Bitcoin_Data_Analysis_with_PyCaret
```


---

## Troubleshooting Git Issues


### If Docker conflicts with existing containers:
```bash
# Remove conflicting containers
docker rm -f bitcoin_analysis

# Verify
docker ps -a | grep bitcoin
```
