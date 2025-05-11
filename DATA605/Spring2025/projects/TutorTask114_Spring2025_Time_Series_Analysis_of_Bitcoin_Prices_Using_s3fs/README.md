---

# 📈 Time Series Analysis of Bitcoin Prices Using s3fs

## 📝 Project Overview  
This project demonstrates a complete time series analysis workflow on Bitcoin prices using real-time data sourced from the CoinGecko API. The data is ingested, stored, and managed using AWS S3 with the help of the `s3fs` Python library. The analysis focuses on trend discovery, visualization, and cloud-based reproducibility.

## 🔧 Technologies Used
- Python 3.9  
- Pandas, Matplotlib, Statsmodels, s3fs  
- CoinGecko API  
- Amazon S3  
- Docker  

## 🚀 Key Features
- Real-time Bitcoin price data ingestion using CoinGecko API  
- Secure storage and retrieval of CSV data files from S3 using `s3fs`  
- Time series decomposition (Trend + Seasonality + Residuals)  
- 5-day moving average forecasting  
- Visualization of trends and smoothed prices  
- Exporting final outputs back to S3  
- Dockerized environment for easy setup

## 🛠️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/kvakada/tutorials.git
cd tutorials/DATA605/Spring2025/projects/TutorTask114_Spring2025_Time_Series_Analysis_of_Bitcoin_Prices_Using_s3fs
```

### 2. Build Docker Image
```bash
docker build -t tutor114 .
```

### 3. Run Jupyter Notebook
```bash
docker run -it -p 8888:8888 -v $(pwd):/app -v ~/.aws:/root/.aws tutor114
```

> 💡 Note: AWS credentials are mounted from your local `~/.aws` directory. Make sure your IAM user has S3 access permissions.

## 📁 File Overview
- `main.ipynb`: Contains all data ingestion, processing, analysis, and visualization
- `bitcoin_prices.csv`: Original data snapshot from API
- `bitcoin_prices_with_forecast.csv`: Final output with 5-day moving average
- `Dockerfile`: Environment containerization setup
- `requirements.txt`: Python dependencies
- `.Trash-0/`, `.ipynb_checkpoints/`: Auto-generated artifacts

## 📊 Sample Outputs
- Daily line chart of Bitcoin prices over the past 30 days  
- Decomposed plots showing trend, seasonality, and residuals  
- Overlay plot of actual price vs. 5-day moving average  

## ✅ Conclusion
The project successfully demonstrates how to:
- Ingest real-time data
- Use cloud-native tools for storage
- Perform reproducible time series analysis
- Visualize and export analysis for future use

## 🔮 Future Enhancements
- Integrate ARIMA/Prophet for predictive modeling  
- Automate with AWS Lambda for regular data updates  
- Add anomaly detection and real-time dashboards  

---



### fetch_bitcoin_data()

This function uses the CoinGecko public API to retrieve Bitcoin price data for the past N days.

- Inputs:
  - `api_key`: your CoinGecko API key
  - `days`: number of days of historical data to fetch
  - `interval`: `daily` or `hourly`

- Returns:
  - A Pandas DataFrame with `Timestamp` and `Price` columns

- Usage:
```python
from bitcoin_utils import fetch_bitcoin_data
df = fetch_bitcoin_data(api_key="YOUR_KEY", days=365)
