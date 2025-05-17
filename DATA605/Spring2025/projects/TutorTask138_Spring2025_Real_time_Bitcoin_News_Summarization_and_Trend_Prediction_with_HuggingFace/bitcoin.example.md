# Bitcoin News Summarization and Trend Prediction with HuggingFace

This project builds a real-time system that ingests Bitcoin-related news, summarizes content using HuggingFace transformers, analyzes sentiment, and predicts Bitcoin prices using a machine learning model (XGBoost). The goal is to bridge NLP and time series forecasting into a single, interpretable pipeline.

## General Guidelines

This project follows the structure and guidelines in the README.It demonstrates how to use the custom API built in bitcoin.API.py (and used in bitcoin.API.ipynb) for:
* Fetching news from NewsAPI
* Summarizing articles using HuggingFace's BART model
* Performing sentiment analysis
* Structuring outputs into daily sentiment scores

### Step-by-Step Explanation

#### 1. Preprocessing Sentiment
Sentiment refers to the emotional tone of the news — whether it’s positive, negative, or neutral.
To use this for modeling, we mapped each category to a numerical value:
POSITIVE → 1
NEUTRAL → 0
NEGATIVE → -1
This allowed us to compute a daily average sentiment score.
##### Example:
Date
Sentiment

2025-05-01
POSITIVE (1)

2025-05-01
NEGATIVE (-1)

→ Daily Sentiment Avg = 0

#### 2. Topic Feature Extraction with TF-IDF

TF-IDF stands for Term Frequency-Inverse Document Frequency. It is a statistical technique that evaluates how important a word is to a document in a collection.
Term Frequency (TF): How often a word appears in a document.
Inverse Document Frequency (IDF): How rare the word is across all documents.
In this context, each day's combined summaries form one document. TF-IDF helps extract the top words (topics) for each day that are both frequent and unique.

##### Example of Extracted Features:

Date
crypto
regulation
mining

...

2025-05-01
0.23
0.15
0.00

...
These numbers indicate how representative the keyword was in that day’s news.

#### 3. Bitcoin Price Data

We retrieved historical Bitcoin prices using the CoinGecko API, a free cryptocurrency price data source. For each date, we collected:
The closing price of Bitcoin (in USD)
We then joined this with the news data using the date field.

##### Example:
Date
Sentiment
crypto
mining
BTC Price

2025-05-01
0.00
0.23
0.00
$63,250

#### 4. Target Variable (Next-Day Price Prediction)

To train a model that can forecast Bitcoin price trends, we shifted the price column by one day to create a "target" — the value we want the model to predict.

This approach assumes that today’s news affects tomorrow’s price.

##### Example Targeting Setup:

Date

Sentiment

...

BTC Price

Target Price (Next Day)

2025-05-01

0.00

...

63,250

63,840

## Result Summary

We trained a gradient-boosted tree model using XGBoost — a high-performance machine learning algorithm ideal for structured/tabular datasets. XGBoost does not require sequence formatting and works well with feature-based learning.

XGBoost was used to learn from daily sentiment and topic signals

The model predicted the next day's Bitcoin price using engineered features

Predicted prices were then compared with actual prices to assess model effectiveness.
## Architecture and Data Flow

The system is built with the following pipeline:
* Ingestion: News articles are fetched from NewsAPI over the past 30 days.
* Summarization: Each article is summarized using HuggingFace's BART (facebook/bart-large-cnn).
* Sentiment Analysis: HuggingFace's sentiment pipeline is applied to the content.
* Time Series Construction: Daily average sentiment scores are calculated.
* Price Integration: Historical BTC price data is fetched from CoinGecko.
* Feature Engineering: Lagged price features, day-of-week, and moving averages are added.
* Prediction: XGBoost is trained to predict next-day BTC prices.
* Forecasting: The model is used to forecast 30 future days.

## Outputs

* bitcoin_100_articles_summary.csv: The result of summarized news with sentiment labels.
* btc_30_day_forecast.csv: The 30-day forward forecast of BTC prices
* xgb_model.pkl: The trained XGBoost model.

## Dashboard

A Streamlit app (streamlit_app.py) provides an interactive dashboard with:

* Latest news and summaries
* Sentiment trends over time
* Forecasted BTC prices
* Date selector to check predictions per day
* Actual vs. predicted graph

This markdown complements bitcoin.example.ipynb and provides the narrative for how the API layer is used in an end-to-end ML pipeline.