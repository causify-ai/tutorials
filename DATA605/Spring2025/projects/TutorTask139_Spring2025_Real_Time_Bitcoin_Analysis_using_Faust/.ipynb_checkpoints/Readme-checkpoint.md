### Name - Pratham Dabas, 121228789
### Github username - perzycodes
### email - pdabas@umd.edu

#  Project - Real-Time Bitcoin Price Analysis using Faust and Kafka

##  Project Overview
This project demonstrates a real-time data streaming and analytics system that monitors Bitcoin (BTC) prices by combining:
- Public data ingestion from the **CoinGecko API**
- Stream processing via **Kafka** and **Faust**
- Live data visualization and statistical analysis in a **Jupyter Notebook**
- Predictive modeling using **ARIMA** to forecast upcoming BTC prices

The system is designed to simulate how modern financial data pipelines operate at scale, providing an end-to-end experience from data collection to real-time dashboards and forecasting.

---

##  Key Objectives
- Implement a **real-time ingestion pipeline** using Faust agents.
- Continuously **monitor Bitcoin prices, volumes, and trends**.
- **Visualize time-series analytics** like moving averages and volatility.
- **Detect significant anomalies** in price behavior (e.g., sharp shifts).
- Integrate an **ARIMA model** for short-term BTC price prediction.

---

##  System Components

| Component | Role |
|----------|------|
| **Kafka + Zookeeper** | Message broker (via Docker) for high-throughput stream ingestion |
| `btc_producer.py` | Producer script that fetches live BTC price data every minute and sends it to Kafka |
| `stream_app.py` | Faust app that consumes data from Kafka topic `btc_prices` and logs it |
| `btc_api.ipynb` | Notebook that visualizes trends, calculates rolling statistics, and forecasts future prices |

---

##  Project Files

| File | Description |
|------|-------------|
| `btc_producer.py` | Retrieves price, volume, and 24h change from CoinGecko API and streams to Kafka |
| `stream_app.py` | Defines a Faust agent that consumes messages and acts as a real-time processor |
| `btc_api.ipynb` | Main dashboard: plots BTC price, volume, moving averages, triggers alerts, and forecasts using ARIMA |
| `docker-compose.yml` | Runs Kafka and Zookeeper services using Docker |
| `requirements.txt` | Lists Python packages needed for running all scripts and notebook |

---

##  Functional Highlights

###  Live Ingestion
- CoinGecko API is queried every 60 seconds.
- Data is formatted and pushed to Kafka topic `btc_prices`.

### Real-Time Processing
- Faust agent consumes the stream.
- Optionally logs or filters abnormal patterns (extensible).

###  Dashboard Features (in `btc_api.ipynb`)
- **Line plot** of BTC/USD price with rolling MA-5, MA-15, MA-30
- **Bar plot** of 24h trading volume
- **Volatility metric** calculated from recent data
- **Alert system** that triggers when price shift exceeds 2%
- **ARIMA model** that predicts next 3 price points (auto-enabled after 20 values)

###  Visual Styling
- Uses `seaborn-darkgrid` theme for a clean professional layout
- Responsive time-axis formatting and real-time refresh

---

##  How to Run This Project

### 1. Set up Python Environment
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Start Kafka + Zookeeper (Docker)
```bash
docker-compose up -d
```

### 3. Run Faust Stream Processor
```bash
faust -A stream_app worker -l info
```

### 4. Start the Kafka Producer
```bash
python btc_producer.py
```

### 5. Open and Run the Visualization Dashboard
```bash
jupyter notebook  # then open btc_api.ipynb and run all cells
```

---

##  What You'll Learn
- End-to-end streaming architecture using Kafka + Faust
- How to query external APIs and convert them into live data feeds
- How to calculate rolling statistics in time series
- How to apply and interpret ARIMA forecasts
- How to design alert systems for anomaly detection

---

##  Sample Outputs
- **Console**:
  ```
  [Analysis (2025-05-17 21:54:37)
   Current Price: $103,267.00
   5-point MA: $103,265.80
   15-point MA: $103,262.47
   30-point MA: $103,258.33
   Volatility: 7.14]

  [ARIMA Forecast] Next 3 BTC Prices: $103,272.10, $103,281.67, $103,288.12
  ```
- **Live plots**: BTC price over time with MA lines, volume bars
- **Alerts**: 
  ```
  [ALERT] Price movement > 2%: 2.31%
  ```

---

##  Future Improvements
- Add persistent storage (e.g., save to a database)
- Enable Faust to compute rolling averages internally
- Extend ARIMA to seasonal models (SARIMA)
- Add a web dashboard (e.g., Streamlit, Dash) for external access

---

##  Dependencies
```
faust-streaming
kafka-python
requests
matplotlib
pandas
statsmodels
```

---

##  Credits
Developed as part of a real-time systems project to demonstrate modern streaming data pipelines using open-source tools.

Instructor feedback and class insights were integrated throughout the development.
