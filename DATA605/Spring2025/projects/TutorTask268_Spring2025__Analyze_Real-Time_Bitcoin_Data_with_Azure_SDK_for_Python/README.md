# Real-Time Bitcoin Streaming & Analysis with Azure and Docker

This project demonstrates a real-time Bitcoin price streaming pipeline using Python, Azure services, and Docker. It ingests data from CoinGecko, streams to Azure Event Hub, stores it in Azure Blob Storage, and performs time series analysis in Azure Synapse and Python notebooks.

---

## What It Does

- Fetches live Bitcoin price data every 60 seconds
- Streams events to Azure Event Hub
- Buffers and stores events in Azure Blob Storage
- Performs time-series analysis (rolling average, MACD, anomalies)
- Runs everything inside a reproducible Docker container

---

## Tech Stack

- Python + Azure SDK (Event Hub, Blob Storage)
- Azure Synapse Analytics
- Docker + PowerShell
- Jupyter Notebook
- CoinGecko API

---

## How to Run

See [docker_instructions.md](./docker_instructions.md) for full setup and commands.

---

## Full Project Walkthrough

For detailed documentation, screenshots, architecture, and code breakdown:  
[project_walkthrough.md](./project_walkthrough.md)

---

## Sample Output

![horly_aggregation](Images/Azure_Synapse/horly_aggregation.png)
