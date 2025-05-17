#!/bin/bash

echo "Phase 1: Fetching Bitcoin Price..."
python scripts/phase1_fetch_bitcoin_prices.py &

sleep 3  # let price fetcher run briefly

echo "Phase 2: Ingesting Price Data to OpenSearch..."
python scripts/phase2_ingest_prices_to_elasticsearch.py

echo "Phase 3: Scraping Crypto News..."
python scripts/phase3_scrape_crypto_news.py &

sleep 3  # let it scrape briefly

echo "Phase 4: Ingesting News to OpenSearch..."
python scripts/phase4_ingest_news_to_elasticsearch.py

echo "Phase 5: Embedding and Indexing Semantic News..."
python scripts/phase5_embed_and_ingest_semantic_news.py

echo "Phase 6: Correlating Anomalies and News..."
python scripts/phase6_anomaly_and_news_correlation.py

echo "All phases complete."
