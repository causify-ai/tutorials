# Real-Time Bitcoin Sentiment Analysis: A Walkthrough of `spacy_selenium_example.ipynb`

## Overview

The `spacy_selenium_example.ipynb` notebook is the core demonstration of the Real-Time Bitcoin Sentiment Analysis pipeline, a project developed for the DATA605 course in Spring 2025. This notebook provides a comprehensive, step-by-step guide to scraping Bitcoin-related tweets from X (Twitter), preprocessing them with spaCy, analyzing sentiment with VADER, correlating sentiment with Bitcoin prices from the CoinGecko API, and visualizing the results. 

Designed for both beginners and intermediate users, this notebook integrates web scraping, natural language processing (NLP), and data visualization to explore whether public sentiment on X influences Bitcoin price movements. It builds on the foundational concepts introduced in `spacy_selenium_API.ipynb` and serves as the main entry point for running the full pipeline, making it an ideal resource for learning practical data science techniques.

## Purpose

The `spacy_selenium_example.ipynb` notebook aims to showcase the complete Bitcoin sentiment analysis pipeline in a single, executable workflow. Its key objectives are to:

- Scrape tweets mentioning "Bitcoin" and "BTC" from X using Selenium.
- Preprocess the tweet text using spaCy for cleaning, tokenization, lemmatization, and entity extraction.
- Analyze sentiment with VADER, categorizing tweets as positive, negative, or neutral.
- Fetch Bitcoin price data from the CoinGecko API and compute correlations with sentiment scores.
- Visualize the results through multiple plots to explore trends and relationships.
- Provide actionable insights and conclusions based on the analysis, along with suggestions for future work.

The notebook includes detailed explanations, beginner-friendly insights, additional examples, and best practices to facilitate learning and experimentation.

## Notebook Structure

The notebook is organized into six steps, each focusing on a critical part of the pipeline:

### 1. Data Ingestion - Scrape Tweets

- **Purpose**: Collect raw tweets mentioning "Bitcoin" or "BTC" from X using the `BitcoinSentimentAnalyzer` class, which leverages Selenium for automated scraping.
- **Process**: Logs into X, searches for tweets, and scrolls dynamically to gather up to 100 tweets, storing them in a pandas DataFrame.
- **Output**: A DataFrame with columns `text` (tweet content) and `timestamp` (when scraped). For example, a tweet might read, "Bitcoin hold become rich."
- **Additional Example**: Filters tweets containing the word "price" to focus on market value discussions, e.g., "Current Bitcoin price: $104542.61 USD."
- **Insights**: Offers troubleshooting tips for common scraping issues like login errors, timeouts, and dynamic content changes, emphasizing the importance of respecting X’s rate limits.

### 2. Data Preprocessing - Clean and Preprocess Tweets

- **Purpose**: Clean and preprocess tweets to prepare them for sentiment analysis.
- **Process**: Uses spaCy to remove noise (URLs, hashtags, emojis), tokenize, lemmatize, and extract entities, followed by VADER sentiment analysis to assign scores and categories.
- **Output**: A DataFrame with columns `text` (processed text), `sentiment` (score from -1 to 1), `sentiment_category` (positive, negative, neutral), and `coins` (identified cryptocurrencies). For example, the processed tweet "bitcoin hold rich" has a sentiment score of 0.5574 (positive).
- **Additional Example**: Analyzes sentiment distribution with a bar chart, showing a mix of 44 neutral, 42 positive, and 14 negative tweets.
- **Insights**: Explains the importance of preprocessing, VADER’s suitability for social media, and spaCy’s NER limitations for crypto terms, with tips for manual experimentation.

### 3. Correlation with Bitcoin Prices - Fetch Prices and Analyze Correlation

- **Purpose**: Fetch Bitcoin price data and correlate it with tweet sentiment to explore relationships.
- **Process**: Retrieves 1-day price history from CoinGecko and computes Pearson (0.0267), Spearman (0.0161), Kendall (0.0101), lagged Pearson (0.0423), and rolling correlations.
- **Output**: A DataFrame combining sentiment and price data, e.g., a sentiment of -0.6369 corresponds to a price of $103,155.60, with a slight price increase (0.000236) in the next interval.
- **Additional Example**: Plots Bitcoin’s price trend over the last day to contextualize the correlation.
- **Insights**: Highlights the very weak positive correlations, suggesting sentiment on X doesn’t strongly predict price movements, and discusses time misalignment challenges.

### 4. Visualizations - Plot Sentiment and Price Trends

- **Purpose**: Visualize the relationship between sentiment and price through various plots.
- **Process**: Generates five plots: a line plot (sentiment vs. price), box plot (sentiment distribution), area plot (cumulative sentiment vs. price), correlation heatmap, and rolling correlation plot.
- **Output**:
  - Line plot: Shows sentiment and price trends, revealing a lack of alignment.
  - Box plot: Displays a wide range of sentiment scores with a median near 0.
  - Area plot: Indicates a rise in cumulative sentiment (to 1.1221) without significant price changes.
  - Heatmap: Confirms weak correlations with pale colors.
  - Rolling correlation plot: Shows volatility, reaching 0.393383 in one window.
- **Additional Guidance**: Provides detailed instructions on reading each plot, e.g., focusing on trends in the line plot and outliers in the box plot.
- **Insights**: Emphasizes the weak relationship between sentiment and price, with tips for spotting patterns and zooming into specific time ranges.

### 5. Cleanup

- **Purpose**: Ensure proper resource management by closing the Selenium WebDriver.
- **Process**: Deletes the `BitcoinSentimentAnalyzer` instance, automatically closing the WebDriver.
- **Additional Example**: Introduces a context manager to safely handle resources, even if errors occur.
- **Insights**: Stresses the importance of avoiding memory leaks, with tips for checking processes and restarting the Jupyter kernel.

### 6. Conclusions and Insights

- **Key Findings**:
  - Sentiment Analysis: A mix of opinions (44 neutral, 42 positive, 14 negative), with a median near 0 and some extreme outliers.
  - Correlation: Very weak positive correlations (e.g., Pearson: 0.0267), indicating X sentiment doesn’t strongly influence price.
  - Visualizations: Show a lack of alignment between sentiment and price trends, with cumulative sentiment rising but price remaining stable.
- **Conclusions**:
  - Weak Sentiment-Price Relationship: Sentiment on X isn’t a strong predictor of Bitcoin price in this sample.
  - Mixed Public Sentiment: Diverse opinions suggest X sentiment is noisy and not a dominant price driver.
  - Time Misalignment: Mismatched timestamps dilute correlations, requiring better alignment in future work.
  - Small Sample Size: 100 tweets limit the robustness of findings; more data could yield better insights.
  - Further Exploration: The slight lagged correlation (0.0423) and outliers suggest potential for deeper analysis.
- **Implications**:
  - Increase sample size to 500–1,000 tweets over a longer period.
  - Incorporate additional metrics like trading volume or market cap.
  - Refine spaCy’s NER and VADER’s thresholds for better accuracy.
  - Account for external events (e.g., news) that might overshadow X sentiment.
  - Explore sentiment from other platforms like Reddit or news articles.

## Educational Value

This notebook is an excellent learning resource for several reasons:

- **Practical Workflow**: Demonstrates a complete pipeline from data collection to visualization, bridging web scraping, NLP, and data analysis.
- **Beginner-Friendly**: Includes detailed explanations, insights, and tips tailored for beginners, such as troubleshooting scraping issues, interpreting sentiment scores, and reading visualizations.
- **Hands-On Examples**: Provides additional examples (e.g., filtering tweets, customizing plots) to encourage experimentation and deeper understanding.
- **Best Practices**: Emphasizes resource management, rate limit considerations, and data quality improvements.
- **Extensibility**: Offers a scalable framework for analyzing other cryptocurrencies or platforms, making it a foundation for further projects.

## How to Use

To run this notebook, follow the setup instructions in the project’s `README.md` to install dependencies, configure ChromeDriver, and provide X credentials. Then:

1. Open the notebook in Jupyter:

   ```bash
   jupyter notebook spacy_selenium_example.ipynb
   ```
2. Run the cells sequentially to execute the pipeline.
3. Experiment with the additional examples (e.g., filter tweets, adjust visualizations) to explore the data further.
4. Review the "Conclusions and Insights" section for key takeaways and future directions.

### Requirements

- Python 3.9+
- ChromeDriver matching your Chrome version
- X (Twitter) account credentials
- Stable internet connection
- Dependencies listed in `requirements.txt`

## Key Takeaways

- The pipeline successfully integrates scraping, NLP, and visualization to analyze Bitcoin sentiment, but the correlation with price is weak (e.g., Pearson: 0.0267).
- Public sentiment on X is diverse, with a mix of positive, neutral, and negative opinions, as seen in the sentiment distribution.
- Visualizations reveal a lack of strong alignment between sentiment and price, suggesting other factors (e.g., market news) may dominate price movements.
- The notebook provides a solid foundation for learning data science techniques, with opportunities for customization and further exploration.

For a deeper understanding of spaCy and Selenium, refer to `spacy_selenium_API.ipynb`. For setup and project context, see the `README.md`.