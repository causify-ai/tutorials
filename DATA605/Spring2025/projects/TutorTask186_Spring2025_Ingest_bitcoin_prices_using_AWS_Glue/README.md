# TutorTask186 – Spring 2025  
## Ingest Bitcoin Prices Using AWS Glue

###  Project Overview

This project demonstrates how to build a serverless ETL pipeline using **AWS Glue** to ingest real-time **Bitcoin price data** from the **CoinGecko API** and process it into columnar format for analysis.

The pipeline includes:
- Fetching JSON data from a public API
- Storing raw data in **Amazon S3**
- Using **AWS Glue Crawler** to discover schema and populate the **Data Catalog**
- Creating a **Glue Job** (written in PySpark) to transform the nested JSON into a flat, partitioned Parquet dataset
- Writing structured outputs back to S3

This project simulates real-world data lake workflows and helps students gain hands-on experience with cloud-based ETL processes.

---

###  Technologies Used

- **AWS Glue** (Crawlers, Jobs, Data Catalog)
- **Amazon S3** for storage
- **CoinGecko API** for real-time price data
- **PySpark** for transformation logic
- **Docker + Jupyter** for local development and simulation

---

###  Files Included

| File | Description |
|------|-------------|
| `template.API.py` | Script to fetch Bitcoin price data from CoinGecko and upload raw JSON to S3 |
| `template.API.ipynb` | Notebook version of the above script |
| `template.example.py` | AWS Glue-compatible PySpark job to read, transform, and write processed data |
| `template.example.ipynb` | Notebook version for local Spark simulation |
| `run_jupyter.sh` | Script to start Jupyter Notebook with Docker |
| `README.md` | Project summary and usage guide |

---

###  ETL Process Breakdown

1. **Data Ingestion**  
   - A script uses `requests` and `boto3` to fetch Bitcoin price history from the CoinGecko API  
   - The data is saved as `bitcoin_prices.json` in the S3 bucket:  
     `s3://data606-bitcoinbucket/raw/`

2. **Schema Discovery**  
   - AWS Glue Crawler scans the raw JSON and registers a table (`raw`) in the `bitcoin_data` database

3. **Data Transformation (Glue Job)**  
   - PySpark script reads the table from the Glue Data Catalog  
   - Explodes the nested JSON array of structs (`prices`)
   - Extracts and converts timestamp, flattens price data
   - Writes the cleaned data in **Parquet format** to:  
     `s3://data606-bitcoinbucket/processed/bitcoin_prices/`  
     (partitioned by date)

---

1. Create a Glue Crawler pointed at `s3://data606-bitcoinbucket/raw/`
2. Create a database named `bitcoin_data`
3. Run the crawler to create the `raw` table
4. Paste the contents of `template.example.py` into a new Glue Job
5. Use an IAM role with permissions for Glue and S3 (e.g., `AWSGlueServiceRole-Bitcoin`)
6. Run the Glue job
7. Check your S3 bucket for processed Parquet files

---

###  Learning Outcomes

- Understand the workflow of ingest → catalog → transform → store
- Work with real API data in cloud-native formats
- Use AWS Glue Data Catalog and PySpark DynamicFrames
- Handle nested JSON and schema inference
- Partition datasets for efficient storage and querying

---

###  Author

Harshit Gadge  
Spring 2025 | University of Maryland  
Course: DATA605 / TutorTask186  
