# 📈 Real-Time Bitcoin Price Analysis with InfluxDB and PyFlink

This project demonstrates a real-time Bitcoin analytics pipeline that fetches live prices, stores them in InfluxDB, and uses NeuralProphet to forecast future prices.

---

## 📁 Folder Structure

```
bitcoin-analytics-project/
│
├── Dockerfile                  # Dockerfile to create the container environment for the app
├── docker-compose.yml          # Defines and runs multi-container Docker apps (InfluxDB + App)
├── .env                        # Stores sensitive env variables like InfluxDB token
│
├── bitcoin_utils.py            # Core API module: fetches live BTC price and computes metrics
│
├── bitcoin.API.ipynb           # Interactive notebook demonstrating usage of the API class
├── bitcoin.Fetch.ipynb         # Notebook showcasing the full pipeline: streaming + forecast
│
├── bitcoin.API.md              # Markdown documentation for the API class and its usage
├── bitcoin.fetch.md            # Full end-to-end markdown doc showing real-time + forecast demo
│
└── README.md                   # Instructions to build, run, and test the entire project
```

---

## ✅ Prerequisites

- Install **Docker** and **Docker Compose**.
- Ensure the following ports are free:
  - `8086` (for InfluxDB)
  - `8888` (for Jupyter Notebook)
- Clone the repository:

```bash
git clone https://github.com/yourusername/bitcoin-price-analysis.git
cd bitcoin-price-analysis
```

---

## 🔧 Step 1: Start InfluxDB (Initial Setup Only)

```bash
docker-compose up influxdb
```

Then, open your browser and go to:  
👉 http://localhost:8086

Complete the setup form using the following:

- **Username**: `admin`  
- **Password**: `admin123`  
- **Organization**: `crypto`  
- **Bucket**: `bitcoin_prices`

### 🎟 Generate Token

1. Go to the **"Data"** section in the left sidebar.
2. Navigate to the **"Tokens"** tab.
3. Click **"Generate Token" → "All-Access Token"**.
4. **Copy the generated token**.

---

## ✍️ Step 2: Save the Token

Paste the token inside your `.env` file:

```
INFLUXDB_TOKEN=<YOUR_GENERATED_TOKEN_HERE>
```

> ⚠️ Do not commit `.env` to GitHub.

---

## 🔄 Step 3: Restart with Full Application

First, shut down InfluxDB:

```bash
Ctrl + C
```

Then clean and restart everything:

```bash
docker-compose down -v
docker-compose up --build
```

---

## 📓 Access Jupyter Notebook

Once up, visit:  
👉 http://localhost:8888

Open and run the following notebooks:

- `bitcoin.API.ipynb`
- `bitcoin.Fetch.ipynb`

---

## 📘 Notebook Summaries

### `bitcoin.API.ipynb`

**Purpose**: Demonstrates how to use the `BitcoinPriceSource` API class.

**What it does**:
- Initializes the price source.
- Iterates over 10 fetches from the CoinGecko API.
- Prints:
  - Timestamped Bitcoin prices
  - Moving Average (MA)
  - Standard Deviation
  - Exponential Moving Average (EMA)
  - Trend and Cumulative Return

---

### `bitcoin.Fetch.ipynb`

**Purpose**: Complete forecast pipeline.

**What it does**:
- Fetches historical BTC data using `yfinance`.
- Trains a `NeuralProphet` model.
- Forecasts prices for the next 365 days.
- Visualizes:
  - Forecasted prices
  - Trend, weekly, and yearly seasonality components
- Prints forecast for the next 7 days.

---