# 📈 Bitcoin-Snowflake Project: Real-time Ingestion, Storage, and Analysis

## 📊 Real-Time Bitcoin Data Analysis with Snowflake

This project demonstrates how to ingest, store, and analyze real-time and historical Bitcoin price data using:

- **🧊 Snowflake** — cloud data warehouse
- **📈 Streamlit** — live analytics dashboard
- **🧪 JupyterLab** — interactive exploration and visualization
- **🐳 Docker** — containerized environment
- **🦎 CoinGecko API** — free source of Bitcoin price data

---

## 🔧 Project Features

- ✅ Fetch 90-day historical BTC prices using CoinGecko API
- ✅ Load data into Snowflake securely using **RSA private key authentication**
- ✅ Perform time-series analysis (Moving Average, Bollinger Bands)
- ✅ Visualize insights with **Streamlit**
- ✅ Access and analyze with **tokenless JupyterLab**
- ✅ Fully containerized with Docker for easy setup

---

## 📁 Directory Structure

```
.
├── btc_dashboard.py                # Streamlit dashboard
├── bitcoin_utils.py                # Utility functions (API, Snowflake)                 
├── docker_data605_style/
│   └── run_all.sh                  # Entrypoint to run Jupyter + Streamlit
│   └── Dockerfile                  # Docker container definition
├── requirements.txt                # Python dependencies
├── rsa_key.pem                     # Your Snowflake RSA private key (secure)
├── .env                            # Environment variables (Snowflake, AWS, etc.)
├── bitcoin.example.ipynb           # End-to-end demo notebook
└── README.md                       # You're reading it!
```

---

## 🚀 Quick Start

> ✅ **Pre-requisite:** Docker must be installed and running on your system

---

### 1. 🔐 Create `.env` file

Copy the example template:

```bash
cp .env.example .env
```

Fill in your values:

```
SNOWFLAKE_ACCOUNT=FKUBIEJ-LYB34847
SNOWFLAKE_USER=SINCHANA2401
SNOWFLAKE_DATABASE=BITCOIN_DB
SNOWFLAKE_SCHEMA=public
SNOWFLAKE_WAREHOUSE=compute_wh
SNOWFLAKE_TABLE=bitcoin_prices
SNOWFLAKE_PRIVATE_KEY=rsa_key.pem

COINGECKO_API_URL=https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd
S3_BUCKET=bitcoin-price-data-bucket
AWS_ACCESS_KEY_ID=AKIAYKFQRAFBBR6W63BX
AWS_SECRET_ACCESS_KEY=l3LxOr+sg244FbddOmSDyhogLAw0GIoRQbNZyLFV
AWS_DEFAULT_REGION=us-east-1
```

> ⚠️ Keep your `.env` file private — it contains credentials.

---

### 2. 🔑 Place RSA Key

Place `rsa_key.pem` (Snowflake private key) in the project root.

> 🔒 **Do not commit this file to GitHub**

---

### 3. 🐳 Build & Run Docker

From your project folder:

```bash
docker build -t btc_snowflake_app -f docker_data605_style/Dockerfile .
```

Run the container:

```bash
docker run -it -p 8888:8888 -p 8502:8502 \
  -v $(pwd):/project --name btc_container btc_snowflake_app
```

---

## 🔍 Access Tools

| Tool       | URL                                         |
|------------|----------------------------------------------|
| 📓 JupyterLab | [http://127.0.0.1:8888/lab/](http://127.0.0.1:8888/lab/) |
| 📊 Streamlit  | [http://localhost:8502](http://localhost:8502)          |

> ✅ Both will launch automatically in the container. No token required for JupyterLab.

---

## 📥 Load Historical BTC Data

Once inside JupyterLab:

```python
from snowflake_utils import load_historical_prices_to_snowflake
load_historical_prices_to_snowflake()
```

---

## 📈 Dashboard Features (Streamlit)

- ✅ **Latest BTC Price**
- ✅ **7-day to 30-day Moving Averages**
- ✅ **Bollinger Bands**
- ✅ **Volatility Insights**
- ✅ **Auto-refresh** via periodic polling (extendable)

---

## 🧪 Development Utilities

| File                  | Purpose                                          |
|-----------------------|--------------------------------------------------|
| `btc_dashboard.py`    | Streamlit app with charts and metrics            |
| `bitcoin_utils.py`    | Python API layer: ingestion, DB insert/query     |
| `bitcoin.example.ipynb` | End-to-end workflow demo in Jupyter             |
| `run_all.sh`          | Shell script launching Jupyter + Streamlit       |

---

## 🔁 Reset / Rebuild Container

```bash
docker rm -f btc_container
docker rmi btc_snowflake_app
```

Then rebuild and rerun.

## To clean or remove image
```bash
bash docker_data605_style/docker_clean.sh
```

---

## 🧯 Troubleshooting

| Issue                        | Fix                                                       |
|-----------------------------|------------------------------------------------------------|
| Streamlit doesn't show up    | Try visiting [http://127.0.0.1:8502](http://127.0.0.1:8502) manually |
| Jupyter asks for token       | Ensure you're using the provided `run_all.sh` script       |
| Snowflake password error     | You must switch to **RSA key-based login** only            |
| RSA key not found error      | Ensure `rsa_key.pem` exists in project root                |

---

## 📦 Optional Enhancements

- 💾 Integrate Snowpipe for automated S3 ingestion
- 📊 Push forecasts into dashboard using Prophet
- 🛠 Deploy Streamlit app using Streamlit Cloud or HuggingFace Spaces
- 🔒 Add secure token authentication for production use

---

## 👩‍💻 Author

Built by **Sinchana Gupta Garla Venkatesha**  
for **DATA605 Spring 2025**

---

> 🧠 Questions or improvements? Create a pull request or issue in the GitHub repo.
