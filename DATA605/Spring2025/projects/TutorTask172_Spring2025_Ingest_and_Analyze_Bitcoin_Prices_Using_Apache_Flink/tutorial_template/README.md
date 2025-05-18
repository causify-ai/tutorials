#  Real-Time Bitcoin Price Analysis with InfluxDB and PyFlink

This project demonstrates a real-time Bitcoin analytics pipeline that fetches live prices, stores them in InfluxDB, and uses NeuralProphet to forecast future prices.

---

##  Folder Structure

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

##  Prerequisites

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
 http://localhost:8086

Complete the setup form using the following:

- **Username**: `admin`  
- **Password**: `admin123`  
- **Organization**: `crypto`  
- **Bucket**: `bitcoin_prices`

###  Generate Token

1. Go to the **"Data"** section in the left sidebar.
2. Navigate to the **"Tokens"** tab.
3. Click **"Generate Token" → "All-Access Token"**.
4. **Copy the generated token**.

---

##  Step 2: Save the Token

Paste the token inside your `.env` file:

```
INFLUXDB_TOKEN=<YOUR_GENERATED_TOKEN_HERE>
```

>  Do not commit `.env` to GitHub.

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
 http://localhost:8888

Open and run the following notebooks:

- `bitcoin.API.ipynb`
- `bitcoin.Fetch.ipynb`

---

##  Notebook Summaries

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
- Uses Pyflink a apache flink framework to extract real time data and print it 
- Fetches historical BTC data using `yfinance`.
- Trains a `NeuralProphet` model.
- Forecasts prices for the next 365 days.
- Visualizes:
  - Forecasted prices
  - Trend, weekly, and yearly seasonality components
- Prints forecast for the next 7 days.


**Why we use two Docker containers for clean separation of concerns:**

- **influxdb_container**: Runs the InfluxDB service to store time-series data.
- **umd_data605_app**: Runs the application (Python + Jupyter + PyFlink) that fetches Bitcoin prices and sends metrics to InfluxDB.

Keeping them separate ensures:

- Each container has a single responsibility.
- Easier debugging, scaling, and maintenance.
- Flexibility to replace or upgrade one service without touching the other.


**Why Docker Network**

Docker containers are isolated by default. To allow them to communicate (e.g., the app pushing data into InfluxDB), we connect them using a custom bridge network (flink_influx_network):
This makes sure:

- The app can reach InfluxDB at http://influxdb_container:8086 (container name acts like a hostname).
- Both services remain discoverable to each other but isolated from the host unless explicitly exposed.



**Why Set Up InfluxDB and Generate Tokens**

- InfluxDB 2.x uses token-based authentication for secure access.
- On first-time setup, we must:
- Run only the InfluxDB container.
- Open http://localhost:8086 and manually:
- Create an admin user, org, and bucket.
- Generate an All-Access Token.
- This token is needed so the app container can authenticate and write metrics to the InfluxDB service securely.
- Once the token is created:
- We store it in a .env file.
- It is automatically injected into the app via docker-compose.yml