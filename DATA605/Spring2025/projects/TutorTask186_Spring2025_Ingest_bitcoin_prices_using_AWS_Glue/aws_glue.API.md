# AWS Glue API Report

## Project Purpose

This file documents the native Python API usage to interact with AWS Glue and related AWS services (like S3), showing how to fetch external data and upload it to AWS.

## Technologies

- CoinGecko API (for Bitcoin prices)
- boto3 (AWS SDK for Python)
- requests (HTTP client)
- SQLite (for local storage testing)

## Key Steps

- Fetch real-time Bitcoin price data using CoinGecko REST API
- Store the raw JSON locally and/or in an S3 bucket using `boto3`
- Generate a local SQLite database using `aws_glue_utils.py`
- Prepare the data to be processed later by Glue jobs

## API Logic Location

All reusable logic (e.g., `upload_to_s3`, `init_filebrowser_db`) is implemented in `aws_glue_utils.py`.

## How to Run

This logic is demonstrated in `aws_glue.API.ipynb`, which:
- Calls CoinGecko's API
- Uploads the data to S3
- Initializes a local DB for development

