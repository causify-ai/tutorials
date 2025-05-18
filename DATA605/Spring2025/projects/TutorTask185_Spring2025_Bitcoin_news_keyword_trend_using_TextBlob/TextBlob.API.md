# Bitcoin News Keyword Analysis API Documentation

This document describes the APIs used in the Bitcoin News Keyword Analysis project, including both the native third-party APIs and our custom wrapper layer.

## Native APIs

### 1. NewsAPI

The project uses [NewsAPI](https://newsapi.org/) to fetch Bitcoin and cryptocurrency-related news articles.

#### Key Endpoints:

- **GET /v2/everything**: Searches through millions of articles from various sources.
  - Parameters:
    - `q`: Search query (e.g., "bitcoin OR cryptocurrency")
    - `from_param`: Start date for articles
    - `to`: End date for articles
    - `language`: Language code (e.g., 'en')
    - `sort_by`: Sort order (e.g., 'publishedAt')
    - `page_size`: Number of results per page (max 100)

#### Rate Limits:
- Free tier: 100 requests per day
- Developer tier: 500 requests per day
- Each request is limited to a maximum of 100 articles

### 2. CoinGecko API

[CoinGecko API](https://www.coingecko.com/api/documentation) is used to fetch Bitcoin price data.

#### Key Endpoints:

- **GET /api/v3/simple/price**: Get current price data
  - Parameters:
    - `ids`: Comma-separated cryptocurrency IDs (e.g., "bitcoin")
    - `vs_currencies`: Conversion currencies (e.g., "usd")
    - `include_market_cap`: Boolean to include market cap data
    - `include_24hr_vol`: Boolean to include 24-hour volume
    - `include_24hr_change`: Boolean to include 24-hour price change percentage

- **GET /api/v3/coins/{id}/market_chart/range**: Get historical price data
  - Parameters:
    - `vs_currency`: Base currency (e.g., "usd")
    - `from`: Unix timestamp for start date
    - `to`: Unix timestamp for end date

#### Rate Limits:
- Free tier: 10-50 calls per minute
- No authentication required, but API key recommended for higher rate limits

## Wrapper API Layer

Our wrapper functions in `TextBlob1_Utils.py` provide simplified access to these APIs with enhanced error handling, rate limit management, and data processing.

### News Data Functions

#### `fetch_bitcoin_news(days=7, query='bitcoin OR cryptocurrency', language='en', sleep_between_days=0.5)`

Fetches Bitcoin-related news articles using NewsAPI, managing rate limits by fetching one day at a time.

- **Parameters**:
  - `days`: Number of days to fetch articles for (default: 7)
  - `query`: Search query to use (default: 'bitcoin OR cryptocurrency')
  - `language`: Language code (default: 'en')
  - `sleep_between_days`: Time to sleep between API calls to avoid rate limits (default: 0.5)
  
- **Returns**: DataFrame containing news articles or None if error

#### `create_query(keywords=None, include_crypto=True, include_bitcoin=True)`

Creates a formatted search query string for the NewsAPI.

- **Parameters**:
  - `keywords`: Additional keywords to include
  - `include_crypto`: Whether to include cryptocurrency terms (default: True)
  - `include_bitcoin`: Whether to include Bitcoin terms (default: True)
  
- **Returns**: Formatted search query string

### Price Data Functions

#### `fetch_current_bitcoin_price()`

Fetches the current Bitcoin price and related metrics with caching to respect rate limits.

- **Returns**: Dictionary with current price data or None if error

#### `fetch_bitcoin_prices(days=30, interval='daily', source='coingecko')`

Fetches historical Bitcoin price data.

- **Parameters**:
  - `days`: Number of days of historical data (default: 30)
  - `interval`: Time interval ('daily', 'hourly') (default: 'daily')
  - `source`: Data source (default: 'coingecko')
  
- **Returns**: DataFrame with price data or None if error

#### `fetch_price_data_alternative(days, interval='daily')`

Alternative method to get Bitcoin price data when the primary API fails.

- **Parameters**:
  - `days`: Number of days of data to generate
  - `interval`: Data interval (default: 'daily')
  
- **Returns**: DataFrame with price data (real or synthetic)

### Keyword Extraction and Analysis

#### `extract_keywords(min_frequency=2, include_titles=True)`

Extracts keywords from news articles using TextBlob.

- **Parameters**:
  - `min_frequency`: Minimum frequency for a keyword to be included (default: 2)
  - `include_titles`: Whether to include article titles in keyword extraction (default: True)
  
- **Returns**: DataFrame with extracted keywords

#### `extract_important_keywords(text, is_title=False)`

Extracts and weights keywords more intelligently.

- **Parameters**:
  - `text`: The text to extract keywords from
  - `is_title`: Whether the text is a title (gives higher weight) (default: False)
  
- **Returns**: List of extracted keywords

#### `analyze_trends(time_window='daily', min_freq=5, min_days=5, verbose=False)`

Analyzes keyword trends over time and correlates with Bitcoin price movements.

- **Parameters**:
  - `time_window`: Time window for aggregation ('daily', 'weekly') (default: 'daily')
  - `min_freq`: Minimum frequency for a keyword to be included (default: 5)
  - `min_days`: Minimum number of different days a keyword must appear (default: 5)
  - `verbose`: Whether to print detailed warnings and processing info (default: False)
  
- **Returns**: DataFrame with keyword trends

### Granger Causality Testing

#### `run_granger_tests(top_n=10, max_lag=3, min_data_points=10)`

Performs Granger causality tests between keyword frequencies and price changes.

- **Parameters**:
  - `top_n`: Number of top keywords to analyze (default: 10)
  - `max_lag`: Maximum lag to test for causality (default: 3)
  - `min_data_points`: Minimum number of data points required (default: 10)
  
- **Returns**: DataFrame with Granger causality test results

#### `run_stationarity_test(series)`

Tests if a time series is stationary using the Augmented Dickey-Fuller test.

- **Parameters**:
  - `series`: The time series to test
  
- **Returns**: Tuple of (is_stationary, p_value)

#### `make_stationary(series)`

Transforms a series to make it stationary.

- **Parameters**:
  - `series`: The time series to transform
  
- **Returns**: The stationary series, or the original if transformation failed

### Visualization Functions

#### `plot_keyword_price_heatmap(top_n=15, save_fig=True, display_fig=False)`

Creates a heatmap showing correlations between keywords and Bitcoin price.

- **Parameters**:
  - `top_n`: Number of top keywords to display (default: 15)
  - `save_fig`: Whether to save the figure (default: True)
  - `display_fig`: Whether to display the figure (default: False)
  
- **Returns**: Boolean indicating success

#### `plot_keyword_vs_price(keyword, save_fig=True, display_fig=False)`

Creates a visualization comparing keyword frequency with Bitcoin price.

- **Parameters**:
  - `keyword`: The keyword to visualize
  - `save_fig`: Whether to save the figure (default: True)
  - `display_fig`: Whether to display the figure (default: False)
  
- **Returns**: Boolean indicating success

#### `generate_keyword_trend_dashboard()`

Generates an interactive dashboard with keyword trends and Bitcoin price data.

- **Returns**: Path to the dashboard HTML file or None if error

## Usage Examples

For comprehensive usage examples, see:

- `BitcoinNews.API.ipynb`: Demonstrates basic API usage
- `BitcoinNews.example.md`: Complete example application
- `BitcoinNews.example.ipynb`: End-to-end functionality demonstration 