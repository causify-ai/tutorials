# spaCy Selenium API Documentation

## Overview

This document outlines the native API functions (spaCy and Selenium) and the wrapper layer implemented in `spacy_utils.py` for the Bitcoin sentiment analysis project. The goal is to provide a clear understanding of the design decisions and intent behind the API usage.

## Native API Usage

### spaCy API
We leverage spaCy for natural language processing (NLP) tasks such as tokenization, lemmatization, and named entity recognition (NER). The choice of spaCy was driven by its efficiency and robust support for English language processing, which is critical for handling social media text like tweets.

- **Tokenization and Lemmatization**: The `nlp()` function processes raw text into a `Doc` object, allowing us to extract tokens and their lemmas. This helps normalize the text (e.g., converting "buying" to "buy") for consistent sentiment analysis.
- **Named Entity Recognition (NER)**: spaCy's `Doc.ents` provides entities with labels like "ORG" or "PRODUCT", which we use to identify mentions of cryptocurrencies (e.g., "Bitcoin"). This enhances the analysis by linking sentiment to specific entities.
- **Design Decision**: We chose spaCy's small English model (`en_core_web_sm`) for its balance of performance and accuracy, suitable for processing short texts like tweets without requiring excessive computational resources.

### Selenium API
Selenium is used for web scraping tweets from X (Twitter), which requires handling dynamic web pages and login requirements.

- **WebDriver Setup**: We initialize a headless Chrome WebDriver with options to disable sandboxing and set a user agent, ensuring compatibility and avoiding detection as a bot.
- **Dynamic Element Loading**: Using `WebDriverWait` and `expected_conditions`, we wait for tweet elements to load, addressing the dynamic nature of X’s search page.
- **Design Decision**: Multiple selectors (e.g., `article[data-testid="tweet"]`, `div[data-testid="tweetText"]`) are tried to handle frequent changes in X’s HTML structure. This robustness ensures the scraper remains functional despite updates to the platform.

## Wrapper Layer in `spacy_utils.py`

The `BitcoinSentimentAnalyzer` class in `spacy_utils.py` wraps the native APIs to provide a streamlined interface for the pipeline.

- **Intent**: Encapsulate complex logic (e.g., Selenium login, spaCy preprocessing) into reusable methods, making the notebooks (`spacy_API.ipynb` and `spacy_example.ipynb`) concise and focused on demonstration.
- **Login Handling**: The `login_to_x` method abstracts the Selenium login process, attempting multiple selectors for username, password, and buttons to ensure compatibility with X’s evolving login page.
- **Preprocessing**: The `preprocess_tweets` method combines text cleaning, tokenization, lemmatization, and NER into a single workflow, reducing the need for repetitive code in notebooks.
- **Design Decision**: By centralizing logic in `spacy_utils.py`, we ensure modularity and maintainability. For example, updates to X’s HTML structure can be handled in one place without modifying the notebooks.

## CoinGecko API Integration
We use the CoinGecko API to fetch Bitcoin price data for correlation analysis.

- **Endpoint**: `https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=1`
- **Method**: GET
- **Purpose**: Retrieves Bitcoin price data over the last day to correlate with tweet sentiment.
- **Design Decision**: The CoinGecko API was chosen for its simplicity and free access, though rate limits are handled by limiting requests to a 1-day period. The `fetch_bitcoin_price` method in `spacy_utils.py` abstracts this interaction, returning a DataFrame for easy integration with sentiment data.

## Usage
The wrapper layer is used in the notebooks to perform tasks like scraping tweets, preprocessing, and sentiment analysis. See `spacy_API.ipynb` for detailed demonstrations of the native APIs and wrapper functions, and `spacy_example.ipynb` for an end-to-end example.

## Notes
- The CoinGecko API is free but may have rate limits.
- Ensure a stable internet connection for API requests.
- Selenium requires a compatible ChromeDriver, which is set up in the Docker container.