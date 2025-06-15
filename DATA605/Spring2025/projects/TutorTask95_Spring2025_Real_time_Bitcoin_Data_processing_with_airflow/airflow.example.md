<!-- toc -->

* [Bitcoin Example Pipeline](#bitcoin-example-pipeline)

  * [Purpose](#purpose)
  * [Notebook Walkthrough](#notebook-walkthrough)

    * [1. Setup & Imports](#1-setup--imports)
    * [2. Fetch Live Bitcoin Price](#2-fetch-live-bitcoin-price)
    * [3. Save, Detect Anomalies & Archive](#3-save-detect-anomalies--archive)
    * [4. Rolling Statistics](#4-rolling-statistics)
    * [5. Visualization](#5-visualization)
    * [6. Upload to S3](#6-upload-to-s3)
  * [Design Philosophy](#design-philosophy)

<!-- tocstop -->

# Bitcoin Example Pipeline

This markdown explains the full implementation demonstrated in `airflow.example.ipynb`. It simulates a local execution of the Bitcoin data pipeline using utility functions designed to be compatible with Apache Airflow.

---

## Purpose

The notebook simulates an end-to-end pipeline execution manually, offering:

* Local testing for Airflow-compatible components
* Visualization of time-series analytics
* Insight into anomaly detection and alerting logic

---

## Notebook Walkthrough

### 1. Setup & Imports

* Environment variables for file paths are configured.
* `bitcoin_utils.py` is reloaded with `importlib` for dynamic updates.
* Logging is enabled for consistent traceability.

### 2. Fetch Live Bitcoin Price

* `fetch_bitcoin_price()` retrieves live Bitcoin pricing from CoinGecko.
* Logs details like price and percentage changes (1h/24h).
* Demonstrates real-time ingestion.

### 3. Save, Detect Anomalies & Archive

* `save_price_to_csv()`:

  * Appends new price to `bitcoin_raw.csv`
  * Detects abnormal price changes
  * Sends Slack alerts for anomalies

* `archive_raw_snapshot()`:

  * Archives current snapshot with a timestamp
  * Optionally uploads to S3 for historical analysis

### 4. Rolling Statistics

* `compute_moving_average(window=3)`:

  * Computes moving average and standard deviation
  * Saves and optionally uploads `bitcoin_processed.csv`

### 5. Visualization

* Multiple Matplotlib plots showcase:

  * Raw prices with moving average and std deviation
  * Annotated timestamps
  * Anomaly thresholds in price change metrics

### 6. Upload to S3

* Final result is uploaded to AWS S3 via `upload_to_s3()`
* Confirms compatibility with cloud deployment

---

This notebook leverages modular logic from `bitcoin_utils.py` to:

* Reduce redundancy
* Promote consistency across DAGs and notebooks
* Improve testability and debugging

---

## Design Philosophy

The pipeline emphasizes:

* **Modularity**: All logic lives in reusable utility functions
* **Observability**: Clear logs and alerting for monitoring
* **Reproducibility**: Timestamped archives and visual tracking
* **Scalability**: Seamless shift from local test to Airflow deployment

---

For deeper insight into the API layer, refer to [`airflow.API.md`](./airflow.API.md).
