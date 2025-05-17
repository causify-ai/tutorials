# Real-Time Bitcoin Sentiment Analysis Using NLTK and Selenium
This tutorial will cover how to fetch
- [Real-Time Bitcoin Sentiment Analysis Using NLTK and Selenium](#real-time-bitcoin-sentiment-analysis-using-nltk-and-selenium)
- [Data Extraction](#data-extraction)
  - [Function: `Progress.__init__(self, current, total)`](#function-progress__init__self-current-total)
  - [Function: `Progress.print_progress(self, current)`](#function-progressprint_progressself-current)
  - [Function: `Scroller.__init__(self, driver)`](#function-scroller__init__self-driver)
  - [Function: `Scroller.scroll_to_bottom()`](#function-scrollerscroll_to_bottom)
  - [Function: `Tweet.__init__(...)`](#function-tweet__init__)
  - [Function: `Twitter_Scraper.__init__(...)`](#function-twitter_scraper__init__)
  - [Function: `_get_driver()`](#function-_get_driver)
  - [Function: `login()`](#function-login)
  - [Function: `scrape_tweets(...)`](#function-scrape_tweets)
  - [Function: `save_to_csv()`](#function-save_to_csv)
  - [Function: `concat_and_save_to_csv(new_data, output_file, poster_details)`](#function-concat_and_save_to_csvnew_data-output_file-poster_details)
  - [Function: `fetch_price()`](#function-fetch_price)
- [Data Transformation](#data-transformation)
  - [Function: `preprocess_text_column(df)`](#function-preprocess_text_columndf)
- [Sentiment Analysis](#sentiment-analysis)
  - [Function: `apply_vader(df, text_col='cleaned_text')`](#function-apply_vaderdf-text_colcleaned_text)
- [Training model](#training-model)
  - [Function: `train_and_evaluate(df, text_col='cleaned_text', label_col='sentiment_label')`](#function-train_and_evaluatedf-text_colcleaned_text-label_colsentiment_label)
- [Data Visualization](#data-visualization)
  - [Function: `plot_sentiment_timeseries(df)`](#function-plot_sentiment_timeseriesdf)
  - [Function: `final_corr()`](#function-final_corr)




# Data Extraction

## Function: `Progress.__init__(self, current, total)`
**Purpose:** Initialize a progress tracking object for scraping tasks. 

**Why:** This function helps visually track scraping progress, especially when collecting large numbers of tweets. 

**Arguments:**  
- `current`: An integer indicating the initial count of scraped tweets.
- `total`: An integer for the total tweets intended to scrape. 
 
**Example Usage:**  
```python
progress = Progress(0, 100)
```

---

## Function: `Progress.print_progress(self, current)`
**Purpose:** Display a dynamic progress bar in the console. 

**Why:** To provide real-time visual feedback of scraping progress. 

**Arguments:**  
- `current`: Integer for current number of tweets scraped.

**Example Usage:**
```python
progress.print_progress(25)
```


---

## Function: `Scroller.__init__(self, driver)`
**Purpose:** Sets up scroll control for dynamic page content.

**Why:** Twitter loads tweets via infinite scroll; this enables controlled scroll actions.

**Arguments:**
- `driver`: Selenium WebDriver to interact with browser window.

**Example Usage:**
```python
scroller = Scroller(driver)
```


---

## Function: `Scroller.scroll_to_bottom()`
**Purpose:** Scroll to different parts of the page.  

**Why:** Necessary to load more tweets dynamically by moving the viewport.

**Example Usage:**
```python
scroller.scroll_to_bottom()
```


---

## Function: `Tweet.__init__(...)`
**Purpose:** Extract data from a single tweet card on the page.  

**Why:** To structure tweet content (text, likes, retweets, etc.) into a usable format.

**Arguments:**
- `card`: Selenium WebElement of the tweet card.  
- `driver`: WebDriver instance to allow interactions.
- `actions`: ActionChains for mouse hover (to extract user metadata).
- `scrape_poster_details`: Boolean to decide whether to extract user stats.
  
**Example Usage:**
```python
tweet = Tweet(card, driver, actions, scrape_poster_details=True)
```


---

## Function: `Twitter_Scraper.__init__(...)`
**Purpose:** Initialize the entire Twitter scraping pipeline.

**Why:** To configure login, scraping strategy (query/hashtag/etc.), and set parameters.

**Arguments:**
- `username`, `password`: For Twitter login.
- `scrape_query`, `scrape_hashtag`, `scrape_username`: Define what to scrape.
- `scrape_latest`, `scrape_top`: Sort tweet results.
- `max_tweets`: Total tweets to collect.

**Example Usage:**
```python
scraper = Twitter_Scraper("myuser", "mypass", scrape_query="Bitcoin", max_tweets=200)
```


---

## Function: `_get_driver()`
**Purpose:** Start and configure the Chrome WebDriver.

**Why:** Required to control the browser and load Twitter.  

**Arguments:** None (internally uses settings).

**Example Usage:** Automatically called during scraper init.


---

## Function: `login()`
**Purpose:** Log into Twitter with credentials.  

**Why:** Required to bypass rate limits and scrape protected content. 

**Arguments:** None. Credentials are passed during init.

**Example Usage:**
```python
scraper.login()
```


---

## Function: `scrape_tweets(...)`
**Purpose:** Collect tweets based on filters (query, user, hashtag).

**Why:** It automates scraping logic including scrolling, card detection, and extraction.

**Arguments:**
- `scrape_query`, `scrape_hashtag`, `scrape_username`: Filters.
- `scrape_latest`, `scrape_top`: Type of results.
- `scrape_poster_details`: Whether to collect user profile info.
- `max_tweets`: Limit of tweets to extract.

**Example Usage:**
```python
scraper.scrape_tweets(scrape_query="Bitcoin", max_tweets=100)
```


---

## Function: `save_to_csv()`
**Purpose:** Save extracted tweets into a timestamped CSV.

**Why:** To persist results for later sentiment analysis or review. 

**Arguments:** None.

**Example Usage:**
```python
scraper.save_to_csv()
```
**Output File:** `./tweets/{timestamp}_tweets_1-{n}.csv`

---

## Function: `concat_and_save_to_csv(new_data, output_file, poster_details)`
**Purpose:** Merge new tweets with an existing dataset, preprocess text, run sentiment analysis, and save results.

**Why:** To update and maintain a unified tweet sentiment dataset.

**Arguments:**
- `new_data`: List of tweets.
- `output_file`: CSV file path to save combined data.
- `poster_details`: Include user info columns or not.

**Example Usage:**
```python
concat_and_save_to_csv(scraper.get_tweets(), poster_details=True)
```
**Output File:** `./tweets/all_tweets.csv`

---

## Function: `fetch_price()`
**Purpose:** Get real-time Bitcoin price from CoinGecko API.

**Why:** To pair tweet sentiment with live BTC price for analysis.

**Arguments:** None.

**Example Usage:**
```python
btc_price = fetch_price()
```


# Data Transformation

## Function: `preprocess_text_column(df)`
**Purpose:** Cleans and tokenizes tweet text for further analysis. 

**Why:** Tweet content contains noise like URLs, mentions, and punctuation. This function standardizes text for better NLP model performance.  

**Arguments:**
- `df`: DataFrame containing a 'Content' column with raw tweet texts. 
  
**Example Usage:**
```python
df = preprocess_text_column(df)
```
**Output File:** Modifies `df` in-place, returns it with `cleaned_text` and `tokens` columns.

---
# Sentiment Analysis

## Function: `apply_vader(df, text_col='cleaned_text')`
**Purpose:** Applies VADER sentiment analysis and labels tweets as positive, negative, or neutral.  

**Why:** To quantify tweet sentiment using compound scores and classify their emotional tone. 

**Arguments:**
- `df`: DataFrame with cleaned text.
- `text_col`: The column to apply sentiment analysis on (default is 'cleaned_text').  

**Example Usage:**
```python
df = apply_vader(df)
```
**Output Files:**
- Updates `df` ineplace, with sentiment scores, labels with Bitcoin price summary

---

# Training model

## Function: `train_and_evaluate(df, text_col='cleaned_text', label_col='sentiment_label')`
**Purpose:** Train a Logistic Regression classifier to predict sentiment labels.  

**Why:** To evaluate how well a machine learning model can classify tweet sentiments.  

**Arguments:**
- `df`: DataFrame with text and sentiment labels.
- `text_col`: Feature column for vectorization.
- `label_col`: Target column for classification.
  
**Example Usage:**
```python
train_and_evaluate(df)
```
**Output File:** None. Prints accuracy and classification report.

---

# Data Visualization

## Function: `plot_sentiment_timeseries(df)`
**Purpose:** Visualizes sentiment trends and distribution over time.  

**Why:** To observe changes in sentiment and how tweet emotions vary with time. 

**Arguments:**
- `df`: Dataframe with sentiment-labeled tweets and Bitcoin prices.  

**Example Usage:**
```python
plot_sentiment_timeseries()
```
**Output File:** None. Displays plots for:
- Average compound score over time.
- Sentiment label distribution over time.

---

## Function: `final_corr()`
**Purpose:** Analyzes correlation between tweet sentiment and Bitcoin price movement.

**Why:** To explore how public sentiment might influence or correlate with BTC price trends. 

**Arguments:** None  

**Example Usage:**
```python
final_corr()
```
**Output File:** None. Displays a heatmap visualizing correlation between sentiment and BTC movement labels (Up, Down, Stable).

---
