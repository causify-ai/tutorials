# Real-Time Bitcoin Price Analysis using Prefect

## Overview

This documentation describes the architecture, components, and Prefect-native API usage in a real-time Bitcoin ETL pipeline. The system ingests Bitcoin price data every 5 minutes, stores it in PostgreSQL, visualizes recent trends, detects price spikes or drops, and sends email alerts. It is designed and orchestrated using **Prefect 2.x**.

---

## Table of Contents

* [Overview](#overview)
* [Architecture Diagram](#architecture-diagram)
* [Project Structure](#project-structure)
* [Environment Variables](#environment-variables)
* [1. Key Prefect Concepts](#1-key-prefect-concepts)

  * [1.1 Flow](#11-flow)
  * [1.2 Task](#12-task)
  * [1.3 Deployment](#13-deployment)
* [2. Task Descriptions](#2-task-descriptions)
* [3. Flow Logic](#3-flow-logic)
* [4. Docker + PostgreSQL Usage](#4-docker--postgresql-usage)
* [5. Visualization & Artifacts](#5-visualization--artifacts)
* [6. Alerting Logic](#6-alerting-logic)
* [7. Execution](#7-execution)
* [8. References](#8-references)

---

## Architecture Diagram

```text
          ┌────────────┐
          │  Prefect   │
          │  Flow      │
          └────┬───────┘
               │
   ┌────────────▼────────────┐
   │  Fetch Bitcoin Price    │ ◄──────────────┐
   └────────────┬────────────┘               │
                │                            │
   ┌────────────▼────────────┐               │
   │   Validate Data         │               │
   └────────────┬────────────┘               │
                │                            │
        ┌───────▼───────────┐                │
        │ Log to Prefect UI │                │
        └───────┬───────────┘                │
                │                            │
   ┌────────────▼────────────┐     ┌─────────▼───────────┐
   │ Visualize + Save Chart  │     │  Save to PostgreSQL │
   └────────────┬────────────┘     └─────────┬───────────┘
                │                            │
                └────────────┬───────────────┘
                             ▼
                     Detect Trends
                          │
                    Email Alerts
```

---

## Project Structure

```
📁 605_Project/
├── prefect_main.py            # Core Prefect flow
├── .env                       # Environment variables
├── Dockerfile                 # Optional: used for reproducibility
├── plot_price_trend.py       # Optional: separate file to view data manually
└── README.md / prefect.API.md
```

## Environment Variables

Stored in `.env` file:

```env
POSTGRES_URL=postgresql+psycopg2://user:password@localhost:5432/bitcoin_etl
ALERT_EMAIL=your_email@gmail.com
EMAIL_APP_PASSWORD=your_generated_app_password
```

---

## 1. Key Prefect Concepts

### 1.1 Flow

Defined using `@flow`. Top-level container coordinating all tasks.

### 1.2 Task

Each step (fetching, validating, saving, plotting) is a `@task`. They can be retried, logged, and orchestrated.

### 1.3 Deployment

Deployed using `.serve()` with interval scheduling every 5 minutes.

---

## 2. Task Descriptions

| Task Name                 | Description                                                              |
| ------------------------- | ------------------------------------------------------------------------ |
| `fetch_bitcoin_price`     | Fetches latest price from CoinGecko API.                                 |
| `validate_data`           | Validates non-null and positive price.                                   |
| `log_to_prefect_artifact` | Creates a Prefect Markdown artifact of the latest price.                 |
| `visualize_price`         | Generates line chart of last 20 price points and uploads as an artifact. |
| `save_to_postgres`        | Saves the timestamped price to PostgreSQL DB.                            |
| `detect_trend`            | Compares latest and previous price to trigger alert on 5% changes.       |
| `send_email_alert`        | Sends email using SMTP over Gmail SSL.                                   |

---

## 3. Flow Logic

```python
@flow
def bitcoin_etl_flow():
    data = fetch_bitcoin_price()
    data = validate_data(data)
    if data:
        log_to_prefect_artifact(data)
        visualize_price(data)
        save_to_postgres(data)
        detect_trend()
```

### Schedule Every 5 Minutes

```python
if __name__ == "__main__":
    bitcoin_etl_flow.serve(
        name="bitcoin-etl-schedule",
        interval=timedelta(minutes=5)
    )
```

---

## 4. Docker + PostgreSQL Usage

```bash
docker run --name bitcoin-postgres \
  -e POSTGRES_USER=sahithivankayala \
  -e POSTGRES_PASSWORD=sahithi2024 \
  -e POSTGRES_DB=bitcoin_etl \
  -p 5432:5432 -d postgres
```

Used to store price data reliably across ETL runs.

---

## 5. Visualization & Artifacts

The `visualize_price` task:

* Queries PostgreSQL for last 20 prices.
* Plots a line chart using `matplotlib`.
* Encodes the image to base64.
* Uploads it as a Prefect artifact in Markdown.

Accessible from the Prefect UI → Run → `Artifacts` tab.

---

## 6. Alerting Logic

If price changes >5% up or down between two consecutive runs:

* Prefect task logs message.
* SMTP email alert sent to configured Gmail using app password.

---

## 7. Execution

To run:

1. Launch Prefect Orion server: `prefect server start`
2. Start Prefect Worker: `prefect worker start --pool default-agent-pool`
3. Run script: `python prefect_main.py`
4. Monitor at: [http://127.0.0.1:4200](http://127.0.0.1:4200)

---

## 8. References

* [Prefect Docs](https://docs.prefect.io/)
* [CoinGecko API](https://www.coingecko.com/en/api/documentation)
* [SQLAlchemy](https://docs.sqlalchemy.org/)
* [Matplotlib](https://matplotlib.org/)
* [PostgreSQL Docker](https://hub.docker.com/_/postgres)
