# 🧠 Time Series Analysis of Bitcoin Prices Using s3fs

**Author:** Karthik Vakada  
**Email:** kvakada@umd.edu  
**Project Tag:** TutorTask114_Spring2025_Time_Series_Analysis_of_Bitcoin_Prices_Using_s3fs  
**Date:** May 2025

---

## 📝 Project Overview

This project demonstrates a reproducible, cloud-native pipeline for analyzing and forecasting Bitcoin prices using Python, ARIMA models, and native S3 access via `s3fs`. Unlike traditional pipelines that rely on static CSVs, this setup dynamically fetches data using the CoinGecko API and writes/reads directly from S3. All code runs inside a standardized Docker environment based on the official `data605_style` template.

---

## 📁 Project Structure

```

TutorTask114\_Spring2025\_Time\_Series\_Analysis\_of\_Bitcoin\_Prices\_Using\_s3fs/
├── bitcoin\_utils.py                      <- Utility functions (fetching, preprocessing, plotting)
├── Spring2025\_s3fs.API.ipynb             <- Notebook demonstrating native s3fs API usage
├── Spring2025\_s3fs.API.md                <- Markdown explanation of native s3 API and use cases
├── Spring2025\_s3fs.API.py                <- Script version of the API notebook
├── Spring2025\_s3fs.example.ipynb         <- Main notebook for end-to-end analysis and modeling
├── Spring2025\_s3fs.example.md            <- Markdown summary of the project pipeline
├── Spring2025\_s3fs.example.py            <- Script version of the example notebook
├── requirements.txt                      <- Standard pip dependencies
├── pyproject.toml                        <- Poetry-based dependency manager
├── Dockerfile                            <- Docker environment setup
├── start.sh                              <- Docker run script
├── dev\_scripts\_tutorial\_s3fs/            <- Boilerplate files from `data605_style`
│   ├── bashrc
│   ├── docker\_build.sh
│   ├── docker\_jupyter.sh
│   ├── docker\_clean.sh
│   ├── docker\_exec.sh
│   ├── docker\_push.sh
│   ├── install\_jupyter\_extensions.sh
│   ├── version.sh
│   └── etc\_sudoers

````

---

## ⚙️ Setup and Dependencies

### Core Dependencies

- Python 3.10+
- `pandas`, `matplotlib`, `statsmodels`, `scikit-learn`
- `s3fs`, `requests`, `seaborn`, `ARIMA`
- Jupyter for notebooks

Install via:

```bash
pip install -r requirements.txt
````

or

```bash
poetry install
```

---

## 🐳 Building and Running the Docker Container

> 🧪 This project uses the `data605_style` Docker template.

```bash
# Go to root
cd TutorTask114_Spring2025_Time_Series_Analysis_of_Bitcoin_Prices_Using_s3fs

# Build image
bash dev_scripts_tutorial_s3fs/docker_build.sh

# Launch notebook
bash dev_scripts_tutorial_s3fs/docker_jupyter.sh
```

📍 Make sure `~/.aws` is available for S3 access.

---

## 🌐 Environment Setup (Non-Docker)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
jupyter lab
```

---

## 🧪 Jupyter Notebooks Overview

### 🔹 Spring2025\_s3fs.API.ipynb

* Connects to S3 using `s3fs`
* Demonstrates listing, reading, writing, and direct `s3://` usage with pandas
* Aligned with [s3fs official examples](https://s3fs.readthedocs.io/en/latest/#examples)

### 🔹 Spring2025\_s3fs.example.ipynb

* Fetches historical Bitcoin data from CoinGecko using `fetch_bitcoin_data()`
* Performs time series decomposition, moving averages, anomaly detection (Z-score)
* Fits ARIMA and log-ARIMA models for forecasting
* Uploads results to S3 using native API

---

## 📷 Sample Output Plots

#### 🔮 Forecast Curve (ARIMA)

![Forecast](figures/bitcoin_forecast_plot.png)

#### 🚨 Anomalies Detected (Z-Score)

![Anomalies](figures/bitcoin_anomalies_plot.png)

---

## 🔐 API Configuration

To fetch Bitcoin data:

```python
from bitcoin_utils import fetch_bitcoin_data
df = fetch_bitcoin_data(days=365)
```

For authenticated S3 access, configure `~/.aws/credentials` or use environment variables.

---

## 📊 Output Summary

* 📈 Daily price trends with moving average
* 📉 Seasonal-Trend decomposition (STL)
* 🚨 Z-score based anomaly detection
* 🔮 Forecasting with ARIMA and log-ARIMA
* ☁️ Dynamic S3 integration for data read/write

---

## 🔁 How to Reproduce This Project

```bash
# Clone the project
git clone https://github.com/YOUR-USERNAME/TutorTask114_Spring2025_Time_Series_Analysis_of_Bitcoin_Prices_Using_s3fs.git
cd TutorTask114_Spring2025_Time_Series_Analysis_of_Bitcoin_Prices_Using_s3fs

# Build and run Docker
bash dev_scripts_tutorial_s3fs/docker_build.sh
bash dev_scripts_tutorial_s3fs/docker_jupyter.sh
```

Or run locally using a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
jupyter lab
```

---

## 💡 Optional Extensions

* Integrate real-time dashboard using Dash or Streamlit
* Use Facebook Prophet for more robust forecasting
* Integrate anomaly alerts via AWS SNS

---

## ✅ Final Notes

This project was developed for **DATA605 – Spring 2025** using the official Causify AI guidelines.
It demonstrates:

* Time series modeling with ARIMA
* Cloud-native data handling via `s3fs`
* Docker-based reproducibility using `data605_style`

📫 Questions? Email: [kvakada@umd.edu](mailto:kvakada@umd.edu)

