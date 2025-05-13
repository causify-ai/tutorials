<!-- toc -->

- [Project Title](#project-title)
  * [Table of Contents](#table-of-contents)
    + [Structure Guide](#structure-guide)
  * [Project Summary](#project-summary)
  * [Technology Stack](#technology-stack)
  * [File Layout](#file-layout)
  * [Execution Instructions](#execution-instructions)
  * [Data Collection](#data-collection)
  * [Analysis Techniques](#analysis-techniques)
  * [Best Practices](#best-practices)

<!-- tocstop -->

# Dagster.example.md

TutorTask102_Spring2025_Real-time_Bitcoin_Data_Ingestion_and_Analysis_with_Dagster


## Project Summary

This project sets up a real-time data pipeline using Dagster to track Bitcoin prices. It uses the CoinGecko API to retrieve the current Bitcoin price at regular intervals and stores this information in a local CSV file. The collected data can then be analyzed to identify trends, compute moving averages, and generate visualizations of price behavior over time.

The project includes automation through scheduled tasks and supports historical backfilling to enable meaningful time series analysis from the start.

## Technology Stack

- Dagster for orchestrating pipelines and handling scheduling
- Requests for API communication
- Pandas for manipulating and cleaning data
- Matplotlib for producing visual insights from trends
- Python 3.9 as the core language
- CSV file storage for persistence and offline access

## File Layout

The structure of the project directory is organized as follows:

- The main directory contains the `bitcoin_pipeline` folder, which holds the pipeline's code logic.
- Asset definitions, jobs, and schedules are modularized into separate files for maintainability.
- Scripts for historical data fetching and time series analysis are kept at the project root.
- Output files, environment settings, and logs are excluded from version control.

The `.gitignore` file ensures that generated and environment-specific files do not pollute the repository.

## Execution Instructions

To use the pipeline:

- Set up and activate a Python virtual environment.
- Install all required dependencies, including Dagster and supporting libraries.
- Launch the Dagster UI to view and run jobs interactively.
- Use the schedule defined in the project to automate price fetching every five minutes.

The UI provides a visual interface to monitor asset execution, view logs, and inspect stored outputs.

## Data Collection

The project connects to the CoinGecko API to pull current Bitcoin price data. Each record includes the timestamp and the price in USD. The data is appended to a CSV file that acts as a time-stamped log of prices.

A dedicated script allows for historical backfilling, enabling the project to start with a full 30-day history of price points at 5-minute intervals. This ensures a robust dataset is available from the beginning for analytical purposes.

## Analysis Techniques

A separate script is used to process the collected data and perform basic time series analysis:

- Moving averages are computed using various window sizes (e.g., 15-minute, 1-hour, 6-hour, and weekly windows).
- Trends are visualized to highlight shifts in price behavior.
- Outputs are saved to disk or displayed via plots for interpretation.

These analyses can help detect volatility, momentum, or stability in the cryptocurrency's value over time.

## Best Practices

- Project logic is modularized to isolate concerns: ingestion, transformation, scheduling, and analysis.
- The environment, logs, and output files are excluded from Git to keep the repository clean.
- The job definition supports retries and is scheduled to run every five minutes.
- Bootstrap data scripts and analysis logic are separated from the live pipeline to maintain clarity and flexibility.

This setup enables both real-time operation and offline experimentation, meeting the goals of reproducibility, automation, and analysis readiness.
