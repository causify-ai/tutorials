# Real-Time Bitcoin Data Pipeline with AWS Batch

This project collects, analyzes, forecasts, and visualizes real-time Bitcoin price data using a fully serverless architecture.

## Technologies Used

- **Python**: Core logic and analysis
- **CoinGecko API**: Live BTC price feed
- **Pandas, Matplotlib, Statsmodels**: Time series analysis & forecasting
- **AWS S3**: Stores raw data and plots
- **Docker**: Containerized the entire pipeline
- **AWS ECR**: Hosted the Docker image
- **AWS Batch (Fargate)**: Executes the pipeline serverlessly

## 🛠 Features

- 🔄 Real-time ingestion of BTC price
- 📈 Trend visualization with moving averages
- 🔮 ARIMA forecasting
- ☁️ Cloud-based CSV and chart storage
- 🧪 Fully testable via `run_pipeline.py`
- 🐳 Production-ready Docker container

## Files

- `ingest.py`: Fetches BTC price
- `analyze.py`: Visualizes price trend
- `forecast.py`: ARIMA forecast
- `upload_to_s3.py`: Sends data to AWS S3
- `run_pipeline.py`: Runs the full pipeline
- Dockerfile: Builds your cloud image

## Example Output

(Screenshots or example charts go here)


Ganesh Vathyaram

**Live and running in the cloud via AWS Batch!**
