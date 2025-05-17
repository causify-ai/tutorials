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

## Features Implemented:

# fetch_live_bitcoin_price()

* Pulls current BTC price every 45s from CoinGecko API

* Stores time-stamped records in data/bitcoin_prices.json

# ingest_prices_to_opensearch()

* Computes % change in price

* Indexes prices with timestamp + pct_change into bitcoin-prices

# scrape_crypto_news()

* Pulls Bitcoin news using CryptoPanic API

* Stores articles in data/crypto_news.json

# embed_and_ingest_semantic_news()

* Uses sentence-transformers to embed news titles

* Indexes into crypto-news-semantic with dense_vector field

# detect_price_anomalies_and_correlate()

* Detects price changes > ±2%

* For each anomaly, retrieves news around that date

* If semantic index exists, does top-3 nearest neighbor retrieval

* Outputs JSON report in results/anomaly_correlation_report.json

# bm25_search() and semantic_vector_search()

* BM25: keyword match from crypto-news

* Vector: cosine similarity from crypto-news-semantic

## OpenSearch Dashboards

# Created visualizations using Kibana (localhost:5601):

* Bitcoin price trend over time

* Anomaly count histogram

* News volume over time

* News titles correlated with price events

# Dashboards use the following index patterns:

* bitcoin-prices

* crypto-news

* crypto-news-semantic

## Dockerized Architecture

The project is fully containerized using docker-compose:

## Services:

elasticsearch: local OpenSearch node on port 9200

kibana: OpenSearch Dashboards on port 5601

bitcoin-worker: for all ingestion scripts

bitcoin-nlp: for embedding & correlation scripts



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

Clone the repository
Enter into the repository

### Start Docker

```bash
docker-compose up --build
```

Ensure Kibana is running at [http://localhost:5601](http://localhost:5601)

---

## Run the Full Pipeline

```bash 
docker cp run_all.sh bitcoin-tutorial-worker:/app/run_all.sh
docker exec -it bitcoin-tutorial-worker bash
chmod +x run_all.sh
bash run_all.sh
```
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

Use `semantic_search_query.py` to find news articles related to the keyword:

```bash
python scripts/semantic_search_query.py
python scripts/bm25_news_search.py
```

## Simple Plot to target Anomalies
```bash
python scripts/plot_price_andanomalies.py
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
