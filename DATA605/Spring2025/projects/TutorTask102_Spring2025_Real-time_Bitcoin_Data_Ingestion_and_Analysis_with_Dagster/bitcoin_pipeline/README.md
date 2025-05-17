<!-- toc -->

* [Project files](#project-files)
* [Setup and Dependencies](#setup-and-dependencies)

  * [Building and Running the Docker Container](#building-and-running-the-docker-container)

    * [Environment Setup](#environment-setup)

<!-- tocstop -->

# Project files

* Author: Suryateja Konduri [ksurya14@umd.edu](mailto:ksurya14@umd.edu)
* Date: 2025-05-17

This project contains the following files

* `README.md`: This file
* `Dagster.API.ipynb`: a notebook describing the Bitcoin API integration
* `Dagster.API.md`: a markdown description of the Bitcoin API
* `Dagster.API.py`: code used for API access
* `Dagster.example.ipynb`: a notebook implementing the pipeline
* `Dagster.example.md`: markdown summary of the pipeline usage
* `Dagster.example.py`: Python script to demonstrate full pipeline
* `Dagster_utils.py`: module containing utility functions like ARIMA forecast, anomaly detection, trend analysis
* `Dockerfile`: builds Dagster environment for this project
* `bitcoin_prices.csv`: CSV file storing real-time price data
* `pyproject.toml`: contains dependency metadata for the project
* `setup.py`: installs the package and all dependencies
* `set_env.sh`: helper script for setting up environment variables

Main Package Folder: `bitcoin_pipeline/bitcoin_pipeline`

* `__init__.py`: package initializer
* `Dagster_utils.py`: shared analysis/forecasting utilities
* `definitions.py`: Dagster `Definitions` object
* `jobs.py`: defines the job combining ops
* `ops.py`: defines data fetching, processing, and forecasting ops
* `schedules.py`: defines 5-minute periodic schedule

# Setup and Dependencies

## Building and Running the Docker Container

* Go to the top of the repo:

  ```bash
  > cd ~/tutorials1/DATA605/Spring2025/projects/TutorTask102_Spring2025_Real-time_Bitcoin_Data_Ingestion_and_Analysis_with_Dagster
  ```

* Build Docker Image:

  ```bash
  > docker build -t dagster-bitcoin-pipeline .
  ```

* Run Container:

  ```bash
  > docker run -it -p 3000:3000 dagster-bitcoin-pipeline
  ```

* Access Dagster UI in browser:

  ```
  http://localhost:3000
  ```

### Environment Setup

If needed, set environment variables in `set_env.sh` and source it before running Dagster locally:

```bash
> source set_env.sh
```

Ensure `DAGSTER_HOME` is set correctly for Dagster instance management.
