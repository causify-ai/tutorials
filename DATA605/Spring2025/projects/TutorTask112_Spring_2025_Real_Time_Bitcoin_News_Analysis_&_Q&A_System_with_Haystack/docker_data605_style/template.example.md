# 📰 Live Bitcoin News Ingestion & Sentiment Pipeline

This document explains the logic used to fetch, clean, and analyze real-time Bitcoin news using the CryptoPanic API.

---

## 🔗 Step 1: Data Source – CryptoPanic API

We use the public [CryptoPanic News API](https://cryptopanic.com/developers/api/) to fetch recent news related to **Bitcoin (BTC)**.

- Endpoint used:  

- Limit: 100 API calls/day (free tier)

---

## 🧼 Step 2: Preprocessing

Each article title is cleaned using `clean_text()`:
- Remove URLs
- Strip special characters
- Normalize whitespace

Example:


---

## 💬 Step 3: Sentiment Analysis

Each article is run through a `transformers` sentiment pipeline:
```python
pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

