# Bitcoin Streaming API Documentation

This document explains the architecture and developer-facing API of a real-time Bitcoin price streaming system built using Azure SDK for Python. The goal is to provide a modular and reusable software layer that cleanly separates logic from execution and supports both synchronous and asynchronous Azure workflows.

---

##  Overview

This project demonstrates a real-time data pipeline using Azure Event Hub and Blob Storage. The system performs the following tasks:

- Continuously fetches the latest Bitcoin price from the CoinGecko API
- Streams that data into Azure Event Hub using a Python script
- Receives and buffers the streamed data using a second script
- After accumulating **50 events**, saves them to Azure Blob Storage as newline-delimited JSON files

To support modular development, we created a shared utility module, `bitcoin_utils.py`, containing all reusable logic and wrappers.

---

##  Architecture

```mermaid
flowchart TD
    A[bitcoin_streamer.py<br>(sync script)] -->|Fetches BTC price<br>from CoinGecko| B[Azure Event Hub]
    B -->|Streams messages| C[bitcoin_receiver.py<br>(async script)]
    C -->|Buffers 50 events<br>in memory| D[Azure Blob Storage<br>(JSON Files)]


During testing or debugging, the batch upload threshold may be temporarily lowered (e.g., to 3 events) to verify that the upload mechanism is working as expected.
