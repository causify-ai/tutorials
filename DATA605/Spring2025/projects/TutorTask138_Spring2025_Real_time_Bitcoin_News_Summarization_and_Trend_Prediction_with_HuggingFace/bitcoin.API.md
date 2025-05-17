# Bitcoin.API.md

## Introduction

This module defines the API layer for fetching, summarizing, and analyzing real-time Bitcoin-related news articles using HuggingFace Transformers and NewsAPI. It enables downstream time series modeling by converting unstructured news into structured daily sentiment records.

---

## Architecture Overview

This API layer consists of the following components:

* **News Fetching:** Uses NewsAPI to pull articles containing the keyword "bitcoin".
* **Summarization:** Applies HuggingFace's BART model to condense article content.
* **Sentiment Analysis:** Classifies each article as POSITIVE, NEGATIVE, or NEUTRAL.
* **Structuring:** Outputs a daily record with title, summary, sentiment, and date.

---
## What is Hugging Face and What Did We Use It For?

Hugging Face is an open-source AI company that provides the transformers library — a high-level interface for using powerful pre-trained models like BERT, GPT, and BART. These models are state-of-the-art in natural language processing (NLP) and are widely used in summarization, classification, and more.

 In this project, Hugging Face was used for:

1. Summarization
Tool: facebook/bart-large-cnn
Functionality: Abstractively condenses long article content to a readable 60-token summary.

Example:
summarizer("Bitcoin hits new high amid economic uncertainty")
##### Output: 'Bitcoin reached a new record as investors sought alternatives amid inflation fears.'

2. Sentiment Analysis
Tool: Hugging Face pipeline('sentiment-analysis')
Functionality: Categorizes news tone into POSITIVE, NEGATIVE, or NEUTRAL.
Example:
sentiment_analyzer("Bitcoin crashes 20% after regulatory crackdown")
##### Output: [{'label': 'NEGATIVE', 'score': 0.99}]

3. Structuring Results:
Tool: Python + Pandas
Functionality: Combines fetched article metadata, summary, and sentiment into a structured DataFrame.
Example Output:
published_date
title
summary
sentiment
source

Example:
2025-05-10
Bitcoin dips on market uncertainty
Bitcoin dropped 5% amid market concerns.
NEGATIVE
CNBC

These tasks transform raw text into structured features for time series analysis.
These two tasks transformed raw text into structured features for time series analysis.

## Setup & Dependencies

```bash
pip install transformers requests pandas python-dotenv
```

Create a `.env` file:

```
NEWSAPI_KEY=your_actual_key_here
```

---

## Function: `get_100_summarized_articles`

Fetches and processes up to 100 Bitcoin-related news articles from the past 30 days.

```python
def get_100_summarized_articles(api_key: str) -> pd.DataFrame:
    """
    Fetch, summarize, and analyze sentiment for Bitcoin news articles.

    Returns:
        pd.DataFrame with columns:
        - published_date
        - title
        - summary
        - sentiment
        - source
    """
```

---

## Workflow Summary

1. **Pull 5 articles/day** from NewsAPI over the past 30 days
2. **Summarize** using `facebook/bart-large-cnn`
3. **Classify sentiment** with HuggingFace pipeline
4. **Return structured DataFrame** ready for time series use

---

## Output Schema

| Column          | Description                           |
| --------------- | ------------------------------------- |
| published\_date | Date of the news article (YYYY-MM-DD) |
| title           | Original headline                     |
| summary         | Generated summary (max 60 tokens)     |
| sentiment       | POSITIVE / NEGATIVE / NEUTRAL         |
| source          | News source name                      |

---

## Example Usage

```python
from bitcoin_utils import get_100_summarized_articles
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("NEWSAPI_KEY")
df = get_100_summarized_articles(api_key=api_key)
df.to_csv("bitcoin_100_articles_summary.csv", index=False)
```

---

## Notes

* Make sure to respect NewsAPI’s 100-requests-per-day rate limit.
* HuggingFace summarization may require internet on first run.
* Articles are filtered for minimum content before summarization.

---

## Designed For

This API module is intended to be used as the input stage for:

* Time series sentiment analysis
* BTC price forecasting
* Dashboard visualizations (Streamlit)

All downstream analytics are conducted in `bitcoin.example.ipynb`.
