# Real-Time Bitcoin Data Processing with Apache Airflow

This project demonstrates a real-time data pipeline built using **Apache Airflow** to fetch, process, and store Bitcoin price data from the **CoinGecko API**. The pipeline includes optional upload to **AWS S3**, making it suitable for real-world data engineering workflows.

---

##  Project Overview

- Fetches real-time Bitcoin price data every hour using Airflow DAGs.
- Saves data to a CSV (`bitcoin_raw.csv`) inside a mounted Docker volume.
- Computes rolling **moving averages** and saves the processed data to `bitcoin_processed.csv`.
- Uploads processed data to **Amazon S3**.
- Designed for **local and Dockerized Airflow environments**.

---

##  File Structure

```plaintext
.
├── dags/
│   └── bitcoin_dag.py           # Airflow DAG defining the pipeline
├── bitcoin_utils.py             # All helper functions (API, processing, upload)
├── bitcoin.API.ipynb            # Demonstrates API usage
├── bitcoin.API.md               # Documents API interface
├── bitcoin.example.ipynb        # Demonstrates pipeline functionality
├── bitcoin.example.md           # Documents the full example
├── data/                        # Mounted volume for storing raw/processed CSVs
├── Dockerfile                   # Custom Airflow image with dependencies
├── requirements.txt             # Python requirements for utils
├── docker-compose.yaml          # Brings up Airflow + Postgres stack
├── docker_build.sh              # Builds Docker container
├── docker_bash.sh               # Accesses webserver container shell
├── docker_jupyter.sh            # Starts Jupyter notebook with mounted workspace
````

---

##  Running the Project

### 1. 🔧 Build and Start the Containers

```bash
./docker_build.sh
docker-compose up -d
```

### 2.  Access Airflow UI

* Visit: [http://localhost:8080](http://localhost:8080)
* Login: `admin` / `admin`
* Trigger the DAG: `bitcoin_data_pipeline`

### 3.  Run Jupyter Notebook (Optional)

```bash
./docker_jupyter.sh
```

Open the URL printed in your terminal to use `bitcoin.API.ipynb` or `bitcoin.example.ipynb`.

---

##  Pipeline Workflow

1. **Fetch Bitcoin Price** – Uses the CoinGecko API.
2. **Save Raw Data** – Appends to a CSV for historical tracking.
3. **Compute Moving Average** – Adds a `price_ma` column.
4. **Upload to S3** – Pushes final data to `s3://bitcoin-price-store/processed/`.

---

##  Environment Notes

* Uses environment variables:

  ```bash
  BITCOIN_RAW_PATH=./data/bitcoin_raw.csv
  BITCOIN_PROCESSED_PATH=./data/bitcoin_processed.csv
  ```
* Supports both Docker and local testing.
* AWS credentials must be available in `~/.aws/credentials`.

---

##  References

* [bitcoin\_utils.py](./bitcoin_utils.py) — all modular logic
* [bitcoin.API.md](./bitcoin.API.md) — API function documentation
* [bitcoin.example.md](./bitcoin.example.md) — architecture and notebook description
* [CoinGecko API](https://www.coingecko.com/en/api)
* [Apache Airflow Docs](https://airflow.apache.org/docs/)


