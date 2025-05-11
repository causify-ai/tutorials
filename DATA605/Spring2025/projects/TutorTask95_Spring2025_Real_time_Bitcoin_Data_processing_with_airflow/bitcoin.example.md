<!-- toc -->

- [Project Title](#project-title)
  * [Table of Contents](#table-of-contents)
  * [General Guidelines](#general-guidelines)
  * [Overview](#overview)
  * [Architecture](#architecture)
  * [Workflow](#workflow)
  * [Technologies Used](#technologies-used)
  * [References](#references)

<!-- tocstop -->

# Project Title

Real-Time Bitcoin Data Processing with Apache Airflow

## Table of Contents

This markdown outlines the full example implementation of a real-time Bitcoin price tracking pipeline using a modular API built around the CoinGecko service.


## General Guidelines

- This file demonstrates how the API functions defined in `bitcoin_utils.py` were used to build and run an end-to-end data pipeline.
- It complements the implementation notebook `bitcoin.example.ipynb`.
- The project is structured using the standard Docker-based setup for DATA605 Spring 2025.

## Overview

The project uses Python and Apache Airflow to create a real-time data pipeline that fetches Bitcoin price data from the CoinGecko API, stores and processes it, and optionally uploads results to AWS S3 for further analytics.

- Data is collected periodically using Airflow DAGs (or manual triggers for testing).
- The processed output includes a moving average of Bitcoin prices.

## Architecture

The project architecture includes the following components:

- **Data Source**: CoinGecko public API
- **Pipeline Logic**: Implemented in `bitcoin_utils.py`
- **Execution Engine**: Apache Airflow running via Docker Compose
- **Storage**:
  - Raw and processed CSVs stored locally (or in Docker volume)
  - Optional upload to S3 for cloud storage and visualization

### Files Used:

- `bitcoin_utils.py`: Contains all reusable utility functions.
- `bitcoin.API.ipynb`: Demonstrates function-level usage of the API.
- `bitcoin.example.ipynb`: Demonstrates full pipeline execution from ingestion to upload.
- `docker-compose.yaml`: Defines service orchestration.
- `.env` or `os.environ` calls: Used to override Airflow paths for local testing.

## Workflow

The notebook `bitcoin.example.ipynb` demonstrates this pipeline flow:

1. **Fetch Bitcoin Price**:
   - Real-time price data fetched using `fetch_bitcoin_price()`.

2. **Save Raw Data**:
   - Data saved/appended to a local CSV using `save_price_to_csv()`.

3. **Compute Moving Average**:
   - `compute_moving_average()` calculates a rolling window average and writes a new CSV.

4. **Plot and Visualize**:
   - Results are visualized using `matplotlib` directly in the notebook.

5. **Optional Upload to S3**:
   - `upload_to_s3()` pushes the final file to a specified AWS S3 path.

## Technologies Used

- Python 3.8+
- Apache Airflow 2.7.3
- CoinGecko API
- Pandas, NumPy, Matplotlib
- AWS S3 (optional)
- Docker & Docker Compose

## References

- [`bitcoin.API.md`](./bitcoin.API.md): Describes each function in the utility module.
- [`bitcoin.example.ipynb`](./bitcoin.example.ipynb): Jupyter notebook implementation of the project.
- [CoinGecko API](https://www.coingecko.com/en/api)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)

