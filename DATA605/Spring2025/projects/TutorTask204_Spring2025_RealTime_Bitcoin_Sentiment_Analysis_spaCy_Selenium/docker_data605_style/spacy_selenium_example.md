<!-- toc -->

- [Project Description](#project-description)
  * [Table of Contents](#table-of-contents)
    + [Architecture and Data](#architecture-and-data)
  * [General Guidelines](#general-guidelines)

<!-- tocstop -->

# Project Description

This project builds a real-time Bitcoin sentiment analysis system using spaCy for natural language processing and Selenium for web scraping. It analyzes tweets to gauge public sentiment and correlates it with Bitcoin price movements, providing visualizations for insights.

## Table of Contents

### Architecture and Data

The application is implemented in `spacy_example.ipynb`, leveraging the `BitcoinSentimentAnalyzer` class from `spacy_utils.py`. The pipeline consists of the following steps:

1. **Data Ingestion**: Scrapes tweets from X (Twitter) using Selenium for keywords "Bitcoin" and "BTC". We chose live tweets to capture real-time sentiment, which is more relevant for market analysis than historical data.
2. **Preprocessing**: Uses spaCy to clean, tokenize, lemmatize, and extract entities from tweets. Named Entity Recognition (NER) identifies cryptocurrency mentions, enhancing sentiment analysis by linking emotions to specific coins.
3. **Sentiment Analysis**: Employs VADER to compute sentiment scores and categorize tweets as positive, negative, or neutral. VADER was selected for its effectiveness with social media text, handling slang and emojis well.
4. **Price Correlation**: Fetches Bitcoin price data from CoinGecko over a 1-day period and computes multiple correlation measures (Pearson, Spearman, Kendall, lagged Pearson, and rolling correlation). These metrics provide a comprehensive view of sentiment-price relationships.
5. **Visualization**: Generates inline plots using Matplotlib, including sentiment vs. price trends, sentiment distribution, cumulative sentiment, correlation heatmaps, and rolling correlations. Inline plotting was chosen to make the analysis interactive and user-friendly.

**Data Sources**:
- **Tweets**: Sourced from X using Selenium, focusing on real-time data for current sentiment.
- **Bitcoin Prices**: Sourced from CoinGecko API, providing hourly price data over 1 day for correlation analysis.

**Design Decisions**:
- **Modularity**: The `BitcoinSentimentAnalyzer` class encapsulates all pipeline logic, ensuring the notebook remains concise and maintainable by calling high-level methods like `scrape_tweets` and `preprocess_tweets`.
- **Real-Time Focus**: Live tweets were prioritized to reflect current market sentiment, critical for financial applications.
- **Correlation Measures**: Multiple metrics were used to provide a nuanced analysis, with lagged correlations exploring predictive relationships.
- **Visualization**: Inline plots eliminate the need for external files, enhancing usability in a Jupyter environment.

## General Guidelines

- This file follows the instructions in [README](/DATA605/DATA605_Spring2025/README.md) for project examples.
- The application leverages the API layer in `spacy_utils.py`, with detailed demonstrations in `spacy_API.ipynb`.
- For a step-by-step walkthrough, see `spacy_example.ipynb`, which executes the full pipeline and displays results.