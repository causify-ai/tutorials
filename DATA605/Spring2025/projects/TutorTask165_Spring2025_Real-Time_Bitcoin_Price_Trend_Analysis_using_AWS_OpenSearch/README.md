# Bitcoin Price Trend Analysis with OpenSearch & Semantic News Correlation

A complete hands-on project to monitor Bitcoin price fluctuations, detect anomalies, and correlate them with semantically relevant news articles using open-source Elasticsearch, Kibana, and Python.

---

## Project Overview

This project demonstrates:

* Time series ingestion of Bitcoin prices via CoinGecko
* News scraping using CryptoPanic API
* Indexing both structured and unstructured data into OpenSearch
* Anomaly detection and semantic news correlation using vector embeddings
* Live dashboards with Kibana

---

## Technologies Used

| Category      | Tool                                      |
| ------------- | ----------------------------------------- |
| Time Series   | CoinGecko API, OpenSearch                 |
| News & Text   | CryptoPanic API, BeautifulSoup (optional) |
| Vector Search | SentenceTransformers + Dense Vectors      |
| Dashboards    | Kibana (OpenSearch Dashboards)            |
| Environment   | Docker Compose                            |

---

## Folder Structure

```
bitcoin-price-analysis/
├── data/                          # JSON files for prices and news
├── results/                       # Anomaly and correlation reports
├── scripts/                       # Individual phase scripts
├── bitcoin_utils.py              # Modular API utilities
├── Bitcoin.API.ipynb             # API layer demonstration
├── Bitcoin.example.ipynb         # Full end-to-end use case
├── Bitcoin.API.md                # Documentation for the API layer
├── Bitcoin.example.md            # Tutorial walkthrough for the example
├── docker-compose.yml            # Container setup
├── Dockerfile                    # Worker container for embeddings/news
└── run_all.sh                    # Pipeline automation script
```

---

## Installation

```bash
git clone https://github.com/yourname/bitcoin-price-analysis.git
cd bitcoin-price-analysis
```

### Start Docker

```bash
docker-compose up --build
```

Ensure Kibana is running at [http://localhost:5601](http://localhost:5601)

---

## Run the Full Pipeline

docker cp run_all.sh bitcoin-tutorial-worker:/app/run_all.sh
docker exec -it bitcoin-tutorial-worker bash
chmod +x run_all.sh
bash run_all.sh

This will:

1. Fetch BTC price (live or historic)
2. Ingest to OpenSearch
3. Scrape and index crypto news
4. Embed news and create semantic index
5. Detect anomalies
6. Correlate with news

---

## Dashboards to Create in Kibana

* Bitcoin Price Over Time (Line Chart)
* Anomaly Events Timeline (Bar/Line)
* News Volume by Day (Bar Chart)
* Filter by pct\_change or anomaly dates

---

## Semantic Search

Use `semantic_search_query.py` to ask questions like:

```bash
python scripts/semantic_search_query.py
# Query: regulation crackdown on bitcoin
```

---

## Documentation

| File                    | Purpose                                      |
| ----------------------- | -------------------------------------------- |
| `Bitcoin.API.md`        | Describes reusable utilities & architecture  |
| `Bitcoin.example.md`    | Step-by-step walkthrough of the full project |
| `bitcoin_utils.py`      | All functions used in notebooks              |
| `Bitcoin.API.ipynb`     | Clean usage demo of the API layer            |
| `Bitcoin.example.ipynb` | Full example notebook (end-to-end)           |

---

## To Do (Optional Enhancements)

* Add authentication for OpenSearch if needed
* Deploy on cloud (e.g., EC2 or GCP)
* Add auto-reload or stream processing for live news

---

## Project Goal

> This repository is structured as a hands-on tutorial for learning OpenSearch, time series pipelines, and LLM-based semantic search.

---
