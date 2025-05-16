# Bitcoin News Keyword Trend Analysis

This project analyzes Bitcoin-related news articles to identify trending keywords and correlate their frequency with Bitcoin price movements over time. It leverages TextBlob for natural language processing and provides both statistical analysis and interactive visualizations.

## Features

- **News Data Collection**: Fetches Bitcoin-related news articles from NewsAPI
- **Keyword Extraction**: Uses TextBlob to extract and analyze meaningful keywords from articles
- **Price Data Integration**: Incorporates Bitcoin price data from CoinGecko API
- **Trend Analysis**: Identifies trending keywords and calculates correlations with price movements
- **Statistical Testing**: Implements Granger causality tests to detect potential lead-lag relationships
- **Interactive Visualization**: Provides both static and interactive charts of the analysis results
- **Dashboard**: Generates a comprehensive HTML dashboard with all visualizations

## Project Structure

```
├── main.py                # Main script to run the complete analysis pipeline
├── fetch_news.py          # Fetches news data from NewsAPI
├── fetch_prices.py        # Retrieves Bitcoin price data from CoinGecko
├── extract_keywords.py    # Extracts keywords using TextBlob
├── analyze_trends.py      # Analyzes keyword trends and correlations
├── granger.py             # Performs Granger causality tests
├── visualize.py           # Creates visualizations of analysis results
├── dashboard/             # Dashboard generation code
│   └── dashboard.py       # Creates interactive HTML dashboard
├── data/                  # Stores intermediate and final data (generated)
├── figures/               # Stores visualizations (generated)
│   └── html/              # Interactive HTML visualizations (generated)
├── requirements.txt       # Python dependencies
└── Dockerfile             # Container definition for Docker deployment
```

## Analysis Pipeline

1. **Data Collection**: 
   - Fetches Bitcoin-related news articles from NewsAPI
   - Retrieves Bitcoin price data from CoinGecko

2. **Keyword Extraction**:
   - Uses TextBlob to process article text
   - Extracts noun phrases and important terms
   - Filters out common stopwords and irrelevant terms
   - Weights keywords by frequency and position (title vs. body)

3. **Trend Analysis**:
   - Identifies trending keywords over time
   - Calculates correlation between keyword frequency and price
   - Aggregates results by time window (daily/hourly)

4. **Statistical Analysis**:
   - Performs Granger causality tests to determine if:
     - Keyword trends precede price movements
     - Price movements precede keyword trends
   - Tests for stationarity and transforms data when necessary

5. **Visualization**:
   - Generates time-series charts of keyword frequencies vs. price
   - Creates correlation heatmaps
   - Visualizes Granger causality test results
   - Compiles an interactive dashboard with all results

## Setup and Installation

### Prerequisites

- Python 3.7+
- NewsAPI key (get one at [newsapi.org](https://newsapi.org/))

### Option 1: Standard Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root with your API key:
   ```
   NEWSAPI_KEY=your_news_api_key
   ```

### Option 2: Docker Installation

1. Clone this repository
2. Create a `.env` file as described above
3. Build the Docker image:
   ```bash
   docker build -t bitcoin-news-analysis .
   ```
4. Run the container:
   ```bash
   docker run --env-file .env -v $(pwd)/figures:/app/figures -v $(pwd)/data:/app/data bitcoin-news-analysis
   ```

## Usage

Run the full analysis pipeline:

```bash
python main.py
```

Or run individual components for testing:

```bash
python fetch_news.py     # Test news API fetching
python fetch_prices.py    # Test price data fetching
python extract_keywords.py # Test keyword extraction
python analyze_trends.py  # Test trend analysis
python granger.py         # Test causality analysis
python visualize.py       # Test visualizations
```

## Example Output

After running the analysis, you'll find:

1. Processed data in the `data/` directory:
   - `bitcoin_news.csv`: Raw news data
   - `bitcoin_news_with_keywords.csv`: News with extracted keywords
   - `bitcoin_prices.csv`: Bitcoin price data
   - `merged_keyword_price.csv`: Joined keyword and price data
   - `keyword_trends.csv`: Keyword trend analysis
   - `granger_causality_results.csv`: Statistical test results

2. Visualizations in the `figures/` directory:
   - Keyword vs. price charts
   - Correlation heatmaps
   - Granger causality test visualizations
   - Interactive HTML versions in `figures/html/`

3. A comprehensive dashboard at `dashboard/index.html`

## API Rate Limits and Sample Data

If you don't have a NewsAPI key or exceed the API rate limits, the program will automatically use sample data for demonstration purposes. This allows you to test the functionality without actual API access.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [TextBlob](https://textblob.readthedocs.io/) for NLP capabilities
- [NewsAPI](https://newsapi.org/) for news data
- [CoinGecko](https://www.coingecko.com/en/api) for price data
- [Plotly](https://plotly.com/) and [Matplotlib](https://matplotlib.org/) for visualizations 