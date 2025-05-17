# Real-time Bitcoin Data Ingestion and Analysis with Dagster

## 📌 Project Overview

This project demonstrates how to use **Dagster**, an open-source data orchestration framework, to build a real-time Bitcoin price ingestion and analysis pipeline.

The system:
- Fetches live Bitcoin price data from the [CoinGecko API](https://www.coingecko.com/en/api)
- Stores the historical data in a CSV file (or optionally in SQLite)
- Performs basic time-series analysis, including moving average calculations
- Visualizes trends for further inspection
- Is built using a modular and reusable Dagster pipeline with `@op` and `@job` patterns

---

## ⚙️ Technologies Used

- **Dagster** – for building and running the pipeline
- **Requests** – for API access
- **Pandas** – for data manipulation and analysis
- **Matplotlib / Plotly** – for visualizing Bitcoin price trends
- **Docker (data605_style)** – for containerized execution
- **Jupyter Notebook** – for demonstration and experimentation

---

## 📂 Project Structure

```bash
Dagster_utils.py           # All functional logic: API calls, saving, analysis
Dagster.API.ipynb          # Minimal example of using the Dagster pipeline
Dagster.API.md             # Markdown explaining the pipeline design
Dagster.example.ipynb      # Full example: ingestion + analysis + visualization
Dagster.example.md         # Markdown explanation of the full example
README.md                  # This file
bitcoin_prices.csv         # Output data file (optional)
pyproject.toml             # Python dependencies declaration
