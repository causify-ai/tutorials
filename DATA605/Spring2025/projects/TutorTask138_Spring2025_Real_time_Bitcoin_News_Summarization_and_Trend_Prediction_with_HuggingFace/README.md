# Real-Time Bitcoin News Summarization and Trend Prediction

This project demonstrates how to fetch real-time Bitcoin news, summarize it using HuggingFace Transformers, analyze sentiment, and apply machine learning for short-term price trend prediction. It is built with reproducibility and tutorial clarity in mind, and it supports two Docker-based development styles.

---

## Project Structure

```
TutorTask138_Spring2025_Real_time_Bitcoin_News_Summarization_and_Trend_Prediction_with_HuggingFace
├── bitcoin_utils.py              # API functions for fetching, summarizing, analyzing
├── bitcoin.API.ipynb             # Demonstrates API layer functionality
├── bitcoin.example.ipynb         # Applies ML model on summarized data
├── bitcoin_100_articles_summary.csv  # Summarized dataset (output from API)
├── README.md                     # This file
├── docker_data605_style/         # Simple student-friendly Docker setup
├── docker_causify_style/         # Thin-layer production-style Docker setup
├── .env                          # Contains NewsAPI key
```

---

## Technology Stack

* **HuggingFace Transformers**: for summarization and sentiment classification
* **NewsAPI**: for fetching Bitcoin-related news headlines
* **TF-IDF (sklearn)**: for extracting top keywords
* **CoinGecko API**: for retrieving historical BTC price data
* **XGBoost**: for predicting next-day Bitcoin prices
* **Docker**: for environment consistency

---

##  Setup Instructions

### 1. Clone the repo:

```bash
git clone --recursive git@github.com:causify-ai/tutorials.git tutorials1
cd tutorials1/DATA605/Spring2025/projects/TutorTask138_Spring2025_Real_time_Bitcoin_News_Summarization_and_Trend_Prediction_with_HuggingFace
```

### 2. Create your `.env` file:

```env
NEWSAPI_KEY=your_actual_newsapi_key_here
```

### 3. Choose Docker Setup

#### Option A: `data605_style` (Recommended for beginners)

```bash
./docker_data605_style/docker_build.sh
./docker_data605_style/docker_jupyter.sh
```

---

## How It Works

### Phase 1 – API Layer

* Fetches news articles about Bitcoin using NewsAPI
* Summarizes each article with `facebook/bart-large-cnn`
* Classifies article sentiment with HuggingFace sentiment pipeline
* Outputs a structured CSV ready for modeling

### Phase 2 – Modeling Layer

* Aggregates daily sentiment and extracts topic keywords (TF-IDF)
* Merges with CoinGecko BTC closing prices
* Trains an XGBoost model to predict the next day’s price
* Plots actual vs predicted prices

---

## Example Outputs

* `bitcoin_100_articles_summary.csv`: contains summarized and labeled news
* Model plots showing actual vs predicted BTC trends

---

## Sample Commands

```python
from bitcoin_utils import get_100_summarized_articles
get_100_summarized_articles(api_key=YOUR_KEY)
```

---

## Key Learnings

* How to use HuggingFace for summarization & sentiment
* How to use TF-IDF for topic detection
* How to train a time-aware XGBoost regressor for financial prediction
* How to structure and containerize an ML project using Docker

---

## Contact & Contributors

Shruthi Raj Gangapuri — \[UMD DATA605 Spring 2025 Project]

This project was completed as part of the Causify-guided tutorial series for Docker and NLP-driven ML systems.

---

##  References

* HuggingFace: [https://huggingface.co/transformers](https://huggingface.co/transformers)
* NewsAPI: [https://newsapi.org](https://newsapi.org)
* CoinGecko API: [https://www.coingecko.com/en/api](https://www.coingecko.com/en/api)
* XGBoost: [https://xgboost.readthedocs.io/en/latest/](https://xgboost.readthedocs.io/en/latest/)
* Causify GitHub: [https://github.com/causify-ai](https://github.com/causify-ai)
