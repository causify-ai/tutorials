# TutorTask186 – Spring 2025  
## Ingest Bitcoin Prices Using AWS Glue

---

## Project Objective

The objective of this project is to demonstrate a real-world data engineering pipeline using AWS Glue and Python APIs. We ingest Bitcoin price data from the public CoinGecko API, store it in an S3 bucket, use AWS Glue Crawler to catalog the data, and finally run a Glue Job using PySpark to transform the nested JSON into a query-ready, columnar format (Parquet), partitioned by date.

---

## Project Architecture

CoinGecko API → S3 (raw) → AWS Glue Crawler → Glue Catalog  
→ AWS Glue Job (PySpark) → S3 (processed Parquet)

### Components:

- CoinGecko API: Provides 30-day historical Bitcoin price data in nested JSON format.
- Amazon S3: Used for both raw input and processed output storage.
- AWS Glue Crawler: Scans the raw JSON and registers its schema into a Glue Data Catalog.
- AWS Glue Job: Processes and flattens the nested JSON using PySpark, converting it to partitioned Parquet.

---

## API Usage and Python Integration

The data ingestion is done via a Python script (template.API.py) using the requests module to hit the CoinGecko endpoint and boto3 to upload the resulting JSON to S3.

The script shows how to interact with AWS services using native Python SDKs, without relying on hardcoded credentials.

---

## AWS Glue Job: PySpark Implementation

The job script (template.example.py / .ipynb) is authored using AWS Glue’s managed PySpark environment. It:

1. Reads data from the Glue Catalog table registered by the crawler
2. Uses explode() to flatten the prices array
3. Extracts and converts timestamps from milliseconds to human-readable format
4. Adds a date column for partitioning
5. Writes the final DataFrame as partitioned Parquet files to S3

This script uses:

from awsglue.context import GlueContext  
from awsglue.utils import getResolvedOptions  
from pyspark.sql.functions import explode, col, to_date

The transformation logic mimics standard ETL practices and makes the dataset more queryable via tools like Athena or Redshift Spectrum.

---

## File Summary

| File                    | Purpose                                                  |
|-------------------------|----------------------------------------------------------|
| template.API.py         | Fetches Bitcoin data from CoinGecko and uploads to S3    |
| template.API.ipynb      | Jupyter version of API ingestion logic                   |
| template.example.py     | Glue-compatible PySpark script for data transformation   |
| template.example.ipynb  | Local simulation of the Glue job using PySpark           |
| aws_glue.example.md     | This report: project overview and API/ETL explanation    |

---

## Learning Outcomes

- Real-time API ingestion using Python
- Native integration with AWS services using boto3
- Writing and running scalable Glue jobs using PySpark
- Handling nested JSON and converting to columnar formats
- Partitioning data to optimize performance for analytics

---

## Author

Harshit Gadge  
University of Maryland – DATA605  
Spring 2025 – TutorTask186
