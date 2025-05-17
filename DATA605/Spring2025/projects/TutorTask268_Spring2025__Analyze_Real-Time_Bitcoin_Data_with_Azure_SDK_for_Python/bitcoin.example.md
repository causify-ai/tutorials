# Real-Time Bitcoin Ingestion with Azure SDK for Python

This tutorial demonstrates how to build a real-time data ingestion pipeline for Bitcoin pricing using the Azure SDK for Python. The pipeline streams data from CoinGecko, sends it to Azure Event Hub, receives it asynchronously, and stores it in Azure Blob Storage — all using clean, modular Python code.

---

## Project Goals

- Ingest real-time Bitcoin price data from the CoinGecko API
- Use Azure Event Hubs to manage high-throughput data streaming
- Store batched data in Azure Blob Storage as newline-delimited JSON
- Build with modular, reusable Python code using the Azure SDK
- Demonstrate the full pipeline through scripts and notebooks

---

## Technology Stack

### Azure SDK for Python

The [Azure SDK for Python](https://learn.microsoft.com/en-us/azure/developer/python/) provides libraries to interact with cloud services like:
- **Azure Event Hub** – for ingesting streaming data
- **Azure Blob Storage** – for scalable cloud file storage
- **Azure Identity** – for secure service-to-service authentication

---

## Architecture Overview

```mermaid
flowchart TD
    A[bitcoin_streamer.py<br>(sync script)] -->|Fetches BTC price<br>from CoinGecko| B[Azure Event Hub]
    B -->|Streams messages| C[bitcoin_receiver.py<br>(async script)]
    C -->|Buffers 50 events<br>in memory| D[Azure Blob Storage<br>(JSON Files)]
```