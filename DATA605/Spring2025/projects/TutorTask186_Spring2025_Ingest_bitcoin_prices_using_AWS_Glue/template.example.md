
## General Guidelines

- This project demonstrates the use of `AWS Glue` and `PySpark` to build an end-to-end ETL pipeline.
- The file follows the markdown structure recommended in [README](/DATA605/DATA605_Spring2025/README.md).
- The API used here is `CoinGecko` for Bitcoin price data.
- Data architecture and transformation logic are described in `template.example.py` and `template.example.ipynb`.

---

## Project Description

This project ingests 30-day historical Bitcoin price data from the CoinGecko public API and stores it in S3. Using AWS Glue Crawlers and Jobs, the raw nested JSON is cataloged, flattened, and stored as partitioned Parquet files for downstream querying.

---

## Technologies Used

- **CoinGecko API** for Bitcoin price data  
- **Amazon S3** for raw and processed data storage  
- **AWS Glue**: Crawlers, Jobs, and Data Catalog  
- **PySpark** for transformation logic  
- **Docker + Jupyter** for local development

---

## Files Included

| File | Description |
|------|-------------|
| `template.API.py` | Script to fetch and upload raw JSON from CoinGecko API to S3 |
| `template.API.ipynb` | Notebook version of the API ingestion |
| `template.example.py` | AWS Glue-compatible PySpark job that performs ETL |
| `template.example.ipynb` | Notebook simulation of the Glue job |
| `run_jupyter.sh` | Shell script to launch Docker-based Jupyter |
| `aws_glue.example.md` | This README file |

---

## ETL Workflow

1. **Ingest**:
   - Use `requests` and `boto3` to call CoinGecko API and upload to `s3://data606-bitcoinbucket/raw/`.

2. **Catalog**:
   - Glue Crawler creates a table (`raw`) under database `bitcoin_data`.

3. **Transform**:
   - Glue Job reads nested JSON from the Glue Catalog.
   - Explodes the array of structs (`prices`) into row-column format.
   - Converts timestamps and adds partition column `date`.

4. **Store**:
   - Final Parquet files are written to  
     `s3://data606-bitcoinbucket/processed/bitcoin_prices/`,  
     partitioned by `date`.

---

## How to Run on AWS

1. Upload raw JSON to S3
2. Create and run a Glue Crawler over `s3://data606-bitcoinbucket/raw/`
3. Create a Glue Job and paste the contents of `template.example.py`
4. Use IAM Role with `s3:PutObject`, `glue:*`, and `s3:GetObject` permissions
5. Run the job and check the output path in S3

---

## Learning Outcomes

- Hands-on use of AWS Glue Data Catalog, Crawlers, and PySpark Jobs
- Flattening nested JSON in a distributed ETL job
- Creating partitioned Parquet files on S3
- Simulating Glue logic locally in Jupyter with Docker

---

## Author

Harshit Gadge  
University of Maryland – DATA605  
Spring 2025 – TutorTask186
