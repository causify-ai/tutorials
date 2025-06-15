
# 📈 Real-Time Bitcoin Data Processing with PyArrow

This project provides a pipeline for ingesting, storing, processing, and analyzing real-time Bitcoin price data using PyArrow, Parquet, and forecasting models like ARIMA.

---

## 📂 Project Structure

```
data_ingestion/
├── datalake/
│   ├── bitcoin_price_stream.parquet       # Historical + real-time BTC data
│   └── load_log.parquet                   # Logging for each ingestion
├── reports/
│   ├── forecast_report.html               # Forecast + financial metrics report
│   ├── forecast_report_forecast.png       # Forecast plot
│   ├── forecast_report_ma.png             # Moving average plot
│   ├── forecast_report_vol.png            # Volatility plot
├── config.py                              # Stores API keys and constants
├── utils.py                               # Core utility functions (fetch, clean, forecast)
├── main.py                                # Main ingestion + report orchestration script
├── ingestion.ipynb                        # Jupyter orchestration + exploration
├── Dockerfile                             # Container setup
├── entrypoint.sh                          # Starts script + Jupyter in container
└── *.sh                                   # Helper scripts for Docker
```

---

## 🚀 Features

- 🔄 **Real-time ingestion** of hourly Bitcoin price data from CoinGecko API
- 🪵 **Automated logging** of ingestion events (`load_log.parquet`)
- 📦 **Storage** in efficient columnar Parquet format using PyArrow
- 📊 **Time series processing**: moving averages, anomalies, volatility
- 📈 **Forecasting**: 30-day forecast with ARIMA
- 📑 **HTML report generation** with plots and summary statistics

---

## ⚙️ Configuration

Edit the `config.py` file to set your CoinGecko API key:

```python
COINGECKO_API_KEY = "your-api-key-here"
```

---

## 🐳 Docker Usage

### ✅ Build the Docker Image

```bash
bash docker_build.sh
```

### ▶️ Run the Container

```bash
bash docker_exec.sh
```

This will:

1. Run `main.py` to ingest data and generate reports
2. Start a Jupyter Notebook server on port `8888`

---

## 📌 Scripts

- `main.py`: Runs full pipeline: ingestion → processing → logging → report
- `entrypoint.sh`: Entry script for Docker container
- `utils.py`: Utility functions for fetching, anomaly detection, ARIMA forecasting
- `run_jupyter.sh`: Starts Jupyter server standalone (if needed)

---

## 📈 Example Output

- `reports/forecast_report.html`: Interactive report
- Includes:
  - 30-day Bitcoin forecast plot
  - Moving averages (7-day, 30-day)
  - Rolling volatility (7-day)
  - Daily return metrics

---

## 📝 How to Run Locally (Outside Docker)

```bash
python main.py
```

Or open `ingestion.ipynb` in Jupyter Notebook for interactive usage.

---

## 📚 Dependencies

All dependencies are defined in the Dockerfile and installed automatically, including:

- `pandas`, `pyarrow`, `requests`
- `matplotlib`, `statsmodels`, `prophet`, `pmdarima`
- `jupyter`, `seaborn`, `plotly`

---

## ✅ Next Steps / TODOs

- [ ] Add unit tests for utility functions
- [ ] Enable email or Slack alerts on forecast/report generation
- [ ] Add support for multiple crypto assets
- [ ] Generate PDF reports with `weasyprint`

---

## 📬 Contact

Maintained by: **Sreevarshini Srinivasan**  
Feel free to reach out for collaboration or questions!
