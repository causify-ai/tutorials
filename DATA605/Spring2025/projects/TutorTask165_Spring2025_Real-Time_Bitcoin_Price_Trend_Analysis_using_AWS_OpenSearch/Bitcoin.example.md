# Bitcoin Price Trends + News Correlation Using ElasticSearch and Semantic Search

Welcome to this 60-minute hands-on tutorial!  
In this guide, you'll learn how to build a system that:

Collects live Bitcoin price data  
Scrapes crypto-related news articles  
Ingests both into OpenSearch  
Detects price anomalies  
Retrieves semantically similar news using vector search  
Visualizes key trends via Kibana or Python

---

## Project Overview

This tutorial demonstrates how to combine time-series data with semantic search to explore how external news influences Bitcoin price fluctuations. We use:

- **OpenSearch** for scalable indexing and vector search
- **CoinGecko API** for price data
- **CryptoPanic API** for news
- **SentenceTransformers** for semantic embeddings
- **Matplotlib/Kibana** for visualization

---

## Project Architecture

```mermaid
graph TD
    A[Fetch BTC price every 1 min] --> B[Append to bitcoin_prices.json]
    B --> C[Ingest to OpenSearch → bitcoin-prices index]

    D[Scrape CryptoPanic News every 1 min] --> E[Append to crypto_news.json]
    E --> F[Ingest to OpenSearch → crypto-news index]

    C --> G[Anomaly Detection]
    G --> H[Correlate with News using Vector Search]
    F --> H
    H --> I[crypto-news-semantic (vector index)]

    I --> J[Kibana Dashboard]
    C --> J

## Prerequisites
Docker and Docker Compose installed

Python 3.10+

API key from https://cryptopanic.com/developers/

.env file in root


# 1. Clone and enter directory
git clone https://github.com/your-org/es-bitcoin
cd es-bitcoin

# 2. Start containers
docker-compose up --build

# 3. Exec into worker container
docker exec -it bitcoin-worker bash

# 4. Run pipeline (you can also use run_all.sh)
python scripts/phase1_fetch_bitcoin_prices.py
python scripts/phase2_ingest_prices_to_elasticsearch.py
python scripts/phase3_scrape_crypto_news.py
python scripts/phase4_ingest_news_to_elasticsearch.py
python scripts/phase5_embed_and_ingest_semantic_news.py
python scripts/phase6_anomaly_and_news_correlation.py

## Sample Dashboard Visuals
1. Bitcoin Price Over Time
Use a line chart on the bitcoin-prices index

Field: timestamp vs price

2. Anomaly Events (Kibana/Matplotlib)
Filter where pct_change > 2% or < -2%

Visualize anomaly counts over time

3. News Volume Over Time
Use crypto-news index

Field: timestamp (daily histogram)

🔍 Semantic Search
We use SentenceTransformers (all-MiniLM-L6-v2) to convert news headlines into dense vectors

Stored in OpenSearch as dense_vector fields

/es-bitcoin/
├── bitcoin_utils.py
├── Bitcoin.API.ipynb
├── Bitcoin.example.ipynb
├── data/
│   ├── bitcoin_prices.json
│   └── crypto_news.json
├── results/
│   ├── anomaly_correlation_report.json
│   └── bitcoin_price_anomalies_plot.png
├── scripts/
│   └── phase1_fetch_bitcoin_prices.py
|   └── phase2_ingest_prices_to_elasticsearch.py
|   └── phase3_scrape_crypto_news.py
|   └── phase4_ingest_news_to_elasticsearch.py
|   └── phase5_embed_and_ingest_semantic_news.py
|   └── phase6_anomaly_and_news_correlation.py
|   └── bm25_news_search.py
|   └── semantic_search_query.py
|   └── plot_price_and_anomalies.py
├── Dockerfile
├── docker-compose.yml
└── .env
