# 🧠 Time Series Analysis of Bitcoin Prices Using s3fs

**Author:** Karthik Vakada  
**Email:** [kvakada@umd.edu](mailto:kvakada@umd.edu)  
**Course:** DATA605 – Spring 2025  
**Live Dashboard:** [bitcoin-price-dashboard.onrender.com](https://bitcoin-price-dashboard.onrender.com)  
**GitHub Repo:** [TimeSeries-Analysis](https://github.com/kvakada/TimeSeries-Analysis)  

---

## 📝 Project Overview

This project presents a **cloud-native, reproducible pipeline** for analyzing and forecasting Bitcoin prices using Python, ARIMA models, and live data integration with AWS S3 through `s3fs`. Forecast results and anomaly detections are displayed in an interactive Plotly dashboard.

---

## 📁 Folder Structure

```

TutorTask114\_Spring2025\_Time\_Series\_Analysis\_of\_Bitcoin\_Prices\_Using\_s3fs/
├── Spring2025\_s3fs.API.ipynb / .md / .py   <- S3 interface usage
├── Spring2025\_s3fs.example.ipynb / .md / .py <- Main pipeline
├── bitcoin\_utils.py / fetch\_bitcoin\_data.py <- Utility scripts
├── Dockerfile / start.sh / docker\_\*.sh      <- Docker setup
├── requirements.txt / pyproject.toml         <- Dependencies
├── figures/
│   ├── bitcoin\_forecast\_plot.png
│   └── bitcoin\_anomalies\_plot.png
├── Bitcoin\_Prices\_Prediction\_Dashboard/     <- Dashboard app (Plotly)
├── dev\_scripts\_tutorial\_s3fs/               <- data605\_style scripts
├── README.md

````

---

## ⚙️ Setup Instructions

### 🔧 Install Requirements (Local)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
jupyter lab
````

### 🐳 Docker Setup (Recommended)

```bash
# Build Docker image
bash dev_scripts_tutorial_s3fs/docker_build.sh

# Launch Jupyter inside Docker
bash dev_scripts_tutorial_s3fs/docker_jupyter.sh
```

> 📌 AWS credentials (`~/.aws/credentials`) are required for S3 access.

---

## 📊 Notebook Overview

### 🔹 `Spring2025_s3fs.API.ipynb`

* Connects to AWS S3 using `s3fs`
* Reads and writes directly to/from `s3://bitcoin-timeseries-data-kv/`

### 🔹 `Spring2025_s3fs.example.ipynb`

* Fetches Bitcoin price data using CoinGecko API
* Preprocesses and analyzes time series
* Detects anomalies (Z-score)
* Forecasts prices using ARIMA and log-ARIMA
* Saves all results back to S3 and CSV

---

## 📷 Output Plots

| Forecast (ARIMA)                    | Anomaly Detection                    |
| ----------------------------------- | ------------------------------------ |
| `figures/bitcoin_forecast_plot.png` | `figures/bitcoin_anomalies_plot.png` |

---

## 🌐 Live Dashboard

Hosted with Plotly Dash (in `/Bitcoin_Prices_Prediction_Dashboard`)
🔗 [View Dashboard](https://bitcoin-price-dashboard.onrender.com)

---

## 📐 Evaluation Metrics

| Model     | RMSE    | MAPE (%) |
| --------- | ------- | -------- |
| ARIMA     | 1520.45 | 6.32%    |
| Log-ARIMA | 1387.62 | 5.94%    |

✔️ **ADF test passed** → Stationary time series (p = 0.003)

---

## 🔁 How to Reproduce

```bash
git clone https://github.com/kvakada/TimeSeries-Analysis.git
cd TutorTask114_Spring2025_Time_Series_Analysis_of_Bitcoin_Prices_Using_s3fs

# Use Docker
bash dev_scripts_tutorial_s3fs/docker_build.sh
bash dev_scripts_tutorial_s3fs/docker_jupyter.sh
```

---

## 🔮 Future Enhancements

* Add trading volume + sentiment data (LSTM, multivariate ARIMA)
* Improve anomaly detection with Isolation Forest
* Migrate to serverless (AWS Lambda)
* Real-time dashboard with WebSocket support

---

## 🙏 Acknowledgment

This project was developed under the **DATA605 Spring 2025** course, using official Causify.AI project templates. Special thanks to reviewers for their detailed feedback and improvements.
