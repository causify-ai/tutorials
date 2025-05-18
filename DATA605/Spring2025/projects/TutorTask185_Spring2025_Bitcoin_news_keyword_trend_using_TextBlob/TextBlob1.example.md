# Bitcoin News Keyword Analysis Example

## Introduction
This document demonstrates how to use the TextBlob library to analyze Bitcoin news articles, extract key insights, and visualize trends in cryptocurrency news coverage.

## Prerequisites
- Python 3.9+
- Required libraries: pandas, matplotlib, textblob, requests, plotly
- API keys for NewsAPI
- Internet connection for API calls

## Example Workflow

### 1. Data Collection
The analysis begins by collecting recent Bitcoin news articles using the NewsAPI and price data from CoinGecko.

```python
# Collect Bitcoin news articles
import TextBlob1_Utils as utils

# Fetch news data for the last 30 days
news_data = utils.fetch_bitcoin_news(days=30, query='bitcoin OR cryptocurrency', language='en')
print(f"Collected {len(news_data)} articles")

# Fetch Bitcoin price data
price_data = utils.fetch_bitcoin_prices(days=30, interval='daily')
```

### 2. Sentiment Analysis
TextBlob analyzes the sentiment of each article's title and description to determine market sentiment.

```python
# Perform sentiment analysis
sentiment_results = utils.analyze_sentiment(news_data)
print(f"Average sentiment polarity: {sentiment_results['avg_polarity']:.2f}")
```

### 3. Keyword Extraction
The system extracts and ranks the most relevant keywords from the corpus of news articles.

```python
# Extract keywords from news content
keywords_df = utils.extract_keywords(news_data)
print("Top keywords:", keywords_df['keyword'].head(10).tolist())
```

### 4. Correlation Analysis
The system correlates keyword frequencies with Bitcoin price movements to identify potential predictive relationships.

```python
# Correlate keywords with price movements
correlation_df = utils.analyze_keyword_price_correlation(keywords_df, price_data)
print("Keywords with highest price correlation:")
print(correlation_df.sort_values('correlation', ascending=False).head(5))
```

### 5. Visualization
The analysis concludes with visualizations that illustrate the relationships between news keywords and price movements.

```python
# Create trend visualizations
utils.plot_keyword_trends(keywords_df, price_data, top_n=5)
utils.plot_keyword_correlation(correlation_df, top_n=10)
```

## Insights from Analysis
- Sentiment in Bitcoin news articles shows moderate correlation with price movements
- Technical terms like "halving", "adoption", and "regulation" often precede price changes
- News volume spikes frequently precede volatility in Bitcoin prices
- Certain keywords show leading indicators for price movements with a 1-3 day lag

## Running the Full Analysis Pipeline
For a complete end-to-end analysis, run the main.py script which executes the full pipeline and generates an interactive dashboard.

```python
# Run the complete analysis pipeline
import main
main.main()
```

The dashboard displays all insights in an interactive format, allowing exploration of the relationship between news coverage and Bitcoin price movements over time.
