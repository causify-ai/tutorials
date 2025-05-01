
# 📈 Real-time Bitcoin Data Ingestion and Analysis with Dagster

This project demonstrates how to build a real-time data ingestion and processing pipeline using [Dagster](https://dagster.io). It collects Bitcoin price data every 5 minutes, stores it in a CSV file, and sets up the foundation for time series analysis and forecasting.

---

## 📁 Project Structure

```
.
├── bitcoin_pipeline/             # Dagster jobs, schedules, and definitions
│   ├── __init__.py
│   ├── jobs.py                   # Dagster job: fetch + process + save
│   ├── schedules.py              # Schedule to run job every 5 minutes
│   └── definitions.py            # Exposes jobs and schedules to Dagster
├── historical_data.py           # Script to bootstrap 1-month historical BTC prices
├── bitcoin_prices.csv           # Output: stored Bitcoin price data
├── pyproject.toml               # Dagster module config
├── .gitignore
└── .dagster_home/               # Dagster instance directory
```

---

## 🛠 Requirements

Install required Python packages in a virtual environment:

```bash
pip install dagster dagit requests pandas matplotlib
```

---

## ⚙️ How the Pipeline Works

### Dagster Job: `bitcoin_price_pipeline`

- **`fetch_bitcoin_price`**: Gets live BTC price using CoinGecko API
- **`process_data`**: Adds a UTC timestamp to the price
- **`save_to_csv`**: Appends the record to `bitcoin_prices.csv`

### Schedule: `bitcoin_price_schedule`

Runs every 5 minutes using this cron:

```cron
*/5 * * * *
```

---

## 🕰 Historical Data Bootstrapping

Run this to get 1 month of backfilled data:

```bash
python historical_data.py
```

This script:
- Pulls `minutely` data for the past 7 days (~5-min intervals)
- Pulls `hourly` data for the past 30 days
- Merges and saves all to `bitcoin_prices.csv`

---

## 🚀 Running Dagster

Start the Dagster dev server:

```bash
source set_env.sh
dagster dev
```

Visit Dagit at: [http://localhost:3000](http://localhost:3000)

---

## 📊 Next Steps

Once your data is collected:
- Visualize BTC trends with matplotlib
- Calculate moving averages
- Forecast future prices with ARIMA, Prophet, etc.

---

## 🧠 Notes for Reviewers / Professors

- The full data pipeline is defined in `bitcoin_pipeline/`
- Live data is ingested every 5 minutes
- `bitcoin_prices.csv` grows over time — ideal for time series analysis
- `historical_data.py` seeds the pipeline with ~2500 rows

---

*Generated on: 2025-05-01 19:48:59*
