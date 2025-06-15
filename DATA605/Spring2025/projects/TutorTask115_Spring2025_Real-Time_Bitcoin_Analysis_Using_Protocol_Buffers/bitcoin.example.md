
# 📘 bitcoin.example.md

This markdown explains the logic and flow of the merged historical + real-time analysis performed in `bitcoin.example.ipynb`.

---

## Objective

Perform a holistic analysis of Bitcoin market data using:
- ⏱️ Historical hourly data (past 30 days)
- 📡 Real-time streamed data (collected every 30 seconds)

---

## Data Source

Both datasets are stored in `.pb` Protobuf format. We use:
- `bitcoin_historical_hourly.pb` (from `load_historical_data.py`)
- `bitcoin_data_YYYY-MM-DD.pb` (from `stream_loop.py`)

---

## Merging Strategy

We load both files, convert them into pandas DataFrames, and concatenate them. We remove duplicate timestamps and sort chronologically.

---

## Analysis Performed

- **24h Price Plot**: Trend of hourly Bitcoin price over the last 24 hours
- **3h Price Plot**: Finer view of recent volatility
- **Daily Summary**: Daily min, max, and mean prices over 30 days
- **Volatility Detection**: Hours with abnormal price range flagged as potential anomalies
- **15-Min Summary**: Snapshot of last 15 minutes (for short-term signal analysis)

---

## Insights Supported

- Detect trends or reversals at daily/hourly/minute levels
- Spot abnormal volatility or spikes
- Support decision making for buying/selling Bitcoin

All charts and tables are generated from the unified `full_df` DataFrame that merges historical and live data.
