# Bitcoin Sentiment Analysis

This project performs real-time Bitcoin sentiment analysis using news data and price information. It combines news sentiment from trusted sources with Bitcoin price data to analyze trends and make price predictions.

## Project Structure

```
.
├── data/               # Directory for storing data files
├── BitcoinSentimentAnalysis.ipynb  # Main analysis notebook
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Setup Instructions

1. Create a virtual environment (recommended):
   ```bash
   python -m venv bitsent
   source bitsent/bin/activate  # On Windows: bitsent\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root with your NewsAPI key:
   ```
   NEWS_API_KEY=your_api_key_here
   ```
   Get your API key from [NewsAPI](https://newsapi.org/)

4. Start Jupyter Notebook:
   ```bash
   jupyter notebook
   ```

5. Open `BitcoinSentimentAnalysis.ipynb` and run the cells in sequence.

## Data Directory

The `data/` directory is used to store:
- News article data
- Bitcoin price data
- Sentiment analysis results
- Forecast results

## Features

- Real-time Bitcoin news fetching from trusted sources
- Historical Bitcoin price data from CoinGecko
- Sentiment analysis using TextBlob
- Time series analysis and price prediction using ARIMA
- Data visualization and reporting

## Dependencies

Major dependencies include:
- pandas
- numpy
- textblob
- statsmodels
- scikit-learn
- newsapi-python
- pycoingecko

For a complete list, see `requirements.txt`.