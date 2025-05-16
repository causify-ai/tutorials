# Bitcoin Sentiment Analysis API Documentation

## Overview
This module (`Bitcoin_API.py`) implements the core functionality of the Bitcoin sentiment analysis pipeline, including scraping tweets, preprocessing with spaCy, sentiment analysis with VADER, price fetching from CoinGecko, correlation analysis, and visualization.

## API Details
- **CoinGecko API for Bitcoin Price**:
  - **Endpoint**: `https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=1`
  - **Method**: GET
  - **Response**: JSON object containing Bitcoin price data over the last day.
    Example:
    ```json
    {
      "prices": [
        [1696118400000, 60000],
        [1696118460000, 60100],
        ...
      ]
    }
    ```

## Usage
The `BitcoinSentimentAnalyzer` class in `Bitcoin_API.py` provides methods for each step of the pipeline:
- `scrape_tweets`: Scrapes tweets using Selenium.
- `preprocess_tweets`: Preprocesses tweets using spaCy and `spacy_utils.py`.
- `analyze_sentiment`: Analyzes sentiment using VADER and categorizes tweets.
- `fetch_bitcoin_price`: Fetches Bitcoin price data from CoinGecko.
- `correlate_sentiment_price`: Correlates sentiment with price.
- `visualize_data`: Visualizes the results.

Run the full pipeline using:
```bash
python Bitcoin_API.py
```

Alternatively, use the Jupyter notebook (`Bitcoin_Sentiment_Analysis.ipynb`) to demonstrate the pipeline step-by-step.

## Notes
- The CoinGecko API is free but may have rate limits.
- Ensure a stable internet connection for API requests.
- Selenium requires a compatible ChromeDriver, which is set up in the Docker container.