# Real-Time Bitcoin News Summarization and Trend Prediction

This document explains how the structured output from the API module was used to generate meaningful time series features and predict Bitcoin price movement using natural language and sentiment signals. The analysis focuses on converting unstructured textual summaries into quantifiable signals and aligning them with actual market data.
This project was developed as part of the DATA605 course at the University of Maryland. It demonstrates a full-stack data science pipeline that incorporates real-time data ingestion, natural language processing using HuggingFace Transformers, sentiment analysis, topic modeling via TF-IDF, and supervised machine learning with XGBoost to model and predict financial trends. It concludes with a deployable Streamlit dashboard to explore news-driven Bitcoin price predictions interactively.

---
# Table of Contents     

Introduction

Dataset Overview

Step-by-Step Explanation

1. Preprocessing Sentiment

2. Topic Feature Extraction with TF-IDF

3. Bitcoin Price Data

4. Target Variable (Next-Day Price Prediction)

Result Summary

Evaluation Metrics

Deployment with Streamlit

Key Insights

## Project Structure

```
TutorTask138_Spring2025_Real_time_Bitcoin_News_Summarization_and_Trend_Prediction_with_HuggingFace
├── bitcoin_utils.py              # API functions for fetching, summarizing, analyzing
├── bitcoin.API.ipynb             # Demonstrates API layer functionality
├── bitcoin.example.ipynb         # Applies ML model on summarized data
├── bitcoin_100_articles_summary.csv  # Summarized dataset (output from API)
├── README.md                     # This file
├── docker_data605_style/         # Simple student-friendly Docker setup
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

#### Option A: `data605_style` 

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
## Dataset Overview

We used the bitcoin_100_articles_summary.csv file, which contains 100 articles with:
Title
Model-generated summary
Sentiment label (POSITIVE / NEGATIVE / NEUTRAL)
Published date
Source
This served as the primary dataset for downstream processing.

The articles were fetched over a span of 30 days using NewsAPI and summarized using the facebook/bart-large-cnn model. Each article was also analyzed for sentiment using HuggingFace’s sentiment classification pipeline. The result was a structured, sentiment-aware, and time-tagged dataset ready for analysis.

## 1. Preprocessing Sentiment

Sentiment refers to the emotional tone of the news — whether it’s positive, negative, or neutral.
To use this for modeling, we mapped each category to a numerical value:
POSITIVE → 1
NEUTRAL → 0
NEGATIVE → -1

## 2. Topic Feature Extraction with TF-IDF

TF-IDF stands for Term Frequency-Inverse Document Frequency. It is a statistical technique that evaluates how important a word is to a document in a collection.
Term Frequency (TF): How often a word appears in a document.
Inverse Document Frequency (IDF): How rare the word is across all documents.
In this context, each day's combined summaries form one document. TF-IDF helps extract the top words (topics) for each day that are both frequent and unique. 

## 3. Bitcoin Price Data

We retrieved historical Bitcoin prices using the CoinGecko API, a free cryptocurrency price data source. For each date, we collected:
The closing price of Bitcoin (in USD)
We then joined this with the news data using the date field.

## 4. Target Variable (Next-Day Price Prediction)
To train a model that can forecast Bitcoin price trends, we shifted the price column by one day to create a "target" — the value we want the model to predict.
This approach assumes that today’s news affects tomorrow’s price.



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

## Deployment with Streamlit

To make this project interactive, we created a Streamlit dashboard that:
Lets users explore article titles, summaries, and sentiment by date
Visualizes daily average sentiment scores over time
Presents predicted vs actual Bitcoin prices
The app reads from the structured CSV file and loads the trained model to show predictions.

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
