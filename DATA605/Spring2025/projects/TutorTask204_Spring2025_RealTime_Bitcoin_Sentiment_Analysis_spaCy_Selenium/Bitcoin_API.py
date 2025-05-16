"""
Analyze Bitcoin sentiment from tweets and correlate with price movements.

1. Citations:
   - Selenium Twitter scraping inspired by: https://github.com/selenium-twitter-scraper
   - VADER sentiment analysis: Hutto, C.J. & Gilbert, E.E. (2014). VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text.
   - CoinGecko API: https://www.coingecko.com/en/api/documentation
2. Run the linter on this script before committing changes to ensure consistency with the coding style.
3. Refer to Bitcoin_API.md for detailed system documentation.

Follow the coding style guide: https://github.com/causify-ai/helpers/blob/master/docs/coding/all.coding_style.how_to_guide.md
"""

# Import libraries in this section.
import logging
import time
from typing import List, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import requests
import spacy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from spacy_utils import clean_text, extract_entities, fetch_coin_list_from_coingecko, match_entities_with_coins
from Bitcoin_utils import log_message

# Set up logger for the module.
_LOG = logging.getLogger(__name__)

# #############################################################################
# Bitcoin Sentiment Analyzer
# #############################################################################

class BitcoinSentimentAnalyzer:
    """
    Analyze sentiment of Bitcoin-related tweets and correlate with price movements.
    """

    def __init__(self, chromedriver_path: str = None, x_username: str = None, x_password: str = None):
        """
        Initialize the BitcoinSentimentAnalyzer.

        :param chromedriver_path: Path to the ChromeDriver executable (optional, defaults to None).
        :param x_username: X username for login (optional, defaults to None).
        :param x_password: X password for login (optional, defaults to None).
        """
        # Initialize spaCy for NLP processing (using spacy_utils).
        self.nlp = spacy.load("en_core_web_sm")
        # Initialize VADER for sentiment analysis.
        self.sid = SentimentIntensityAnalyzer()
        # Fetch coin list from CoinGecko for entity matching.
        self.coin_list = fetch_coin_list_from_coingecko()
        # Store X credentials
        self.x_username = x_username
        self.x_password = x_password
        # Set up Selenium WebDriver in headless mode.
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
        if chromedriver_path:
            service = Service(chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            self.driver = webdriver.Chrome(options=chrome_options)

    def login_to_x(self):
        """
        Log in to X using provided credentials.
        """
        if not self.x_username or not self.x_password:
            log_message("No X credentials provided. Attempting anonymous access.")
            return

        log_message("Logging in to X...")
        self.driver.get("https://x.com/login")
        time.sleep(5)  # Wait for login page to load

        try:
            # Enter username
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "text"))
            )
            username_field.send_keys(self.x_username)
            next_button = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Next')]")
            next_button.click()
            time.sleep(2)

            # Enter password
            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_field.send_keys(self.x_password)
            login_button = self.driver.find_element(By.XPATH, "//span[contains(text(), 'Log in')]")
            login_button.click()
            time.sleep(5)  # Wait for login to complete

            log_message("Successfully logged in to X.")
        except Exception as e:
            log_message(f"Failed to log in to X: {str(e)}")
            self.driver.save_screenshot("login_failure_screenshot.png")
            log_message("Screenshot of login failure saved as login_failure_screenshot.png")
            raise

    def scrape_tweets(self, keyword: str, max_tweets: int) -> List[dict]:
        """
        Scrape tweets containing the specified keyword using Selenium.

        :param keyword: The search term to query on Twitter (e.g., "Bitcoin").
        :param max_tweets: The maximum number of tweets to scrape.
        :return: A list of dictionaries with tweet text and timestamp.
        """
        log_message(f"Scraping tweets for keyword: {keyword}")

        # Log in to X if credentials are provided
        self.login_to_x()

        # Navigate to the search page
        self.driver.get(f"https://x.com/search?q={keyword}&src=typed_query&f=live")
        time.sleep(5)  # Wait for initial page load

        tweets = []
        scroll_attempts = 0
        max_scroll_attempts = 50  # Limit to avoid infinite scrolling

        while len(tweets) < max_tweets and scroll_attempts < max_scroll_attempts:
            try:
                # Wait for tweet elements to be present (increased timeout to 30 seconds)
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'article[data-testid="tweet"]'))
                )
                tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]')
                for element in tweet_elements:
                    try:
                        text = element.find_element(By.CSS_SELECTOR, 'div[lang]').text
                        timestamp = pd.Timestamp.now().isoformat()
                        if text not in [t["text"] for t in tweets]:
                            tweets.append({"text": text, "timestamp": timestamp})
                    except:
                        continue

                # Scroll down to load more tweets
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Wait for new tweets to load
                scroll_attempts += 1

            except TimeoutException as e:
                log_message("Timeout waiting for tweet elements. Debugging info:")
                log_message(f"Page URL: {self.driver.current_url}")
                log_message("Page source snippet:")
                page_source = self.driver.page_source
                log_message(page_source[:1000])
                self.driver.save_screenshot("timeout_screenshot.png")
                log_message("Screenshot saved as timeout_screenshot.png")
                raise e

        log_message(f"Scraped {len(tweets)} tweets.")
        return tweets[:max_tweets]

    def preprocess_tweets(self, tweets: List[dict]) -> List[dict]:
        """
        Preprocess tweets using spaCy for tokenization, lemmatization, and cleaning.

        :param tweets: A list of tweet dictionaries with text and timestamp.
        :return: A list of preprocessed tweet dictionaries with entities.
        """
        log_message(f"Preprocessing {len(tweets)} tweets.")
        processed_tweets = []
        for tweet in tweets:
            # Clean the text using spacy_utils
            cleaned_text = clean_text(tweet["text"])
            doc = self.nlp(cleaned_text)
            tokens = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct]
            processed_text = " ".join(tokens)
            # Extract entities and match with coins
            entities = extract_entities(cleaned_text, self.nlp)
            matched_coins = match_entities_with_coins(entities, self.coin_list)
            processed_tweets.append({
                "text": processed_text,
                "timestamp": tweet["timestamp"],
                "entities": entities,
                "coins": matched_coins
            })
        log_message("Completed preprocessing.")
        return processed_tweets

    def analyze_sentiment(self, tweets: List[dict]) -> List[dict]:
        """
        Analyze the sentiment of tweets using VADER and categorize them.

        :param tweets: A list of preprocessed tweet dictionaries.
        :return: A list of tweet dictionaries with sentiment scores and categories.
        """
        log_message(f"Analyzing sentiment for {len(tweets)} tweets.")
        for tweet in tweets:
            sentiment = self.sid.polarity_scores(tweet["text"])
            tweet["sentiment"] = sentiment["compound"]
            # Categorize sentiment
            if tweet["sentiment"] > 0:
                tweet["sentiment_category"] = "positive"
            elif tweet["sentiment"] < 0:
                tweet["sentiment_category"] = "negative"
            else:
                tweet["sentiment_category"] = "neutral"
        log_message("Sentiment analysis complete.")
        return tweets

    def fetch_bitcoin_price(self) -> pd.DataFrame:
        """
        Fetch Bitcoin price data from CoinGecko API.

        :return: A pandas DataFrame with columns 'timestamp' and 'price'.
        """
        log_message("Fetching Bitcoin price data from CoinGecko API.")
        url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=1"
        response = requests.get(url).json()
        prices = response["prices"]
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        log_message(f"Fetched {len(df)} price data points.")
        return df

    def correlate_sentiment_price(self, tweets: List[dict], price_df: pd.DataFrame) -> Tuple[pd.DataFrame, float]:
        """
        Correlate sentiment scores with Bitcoin price data.

        :param tweets: A list of tweet dictionaries with sentiment scores.
        :param price_df: A DataFrame with Bitcoin price data.
        :return: A tuple containing the combined DataFrame and the correlation coefficient.
        """
        log_message("Correlating sentiment with Bitcoin price.")
        sentiment_df = pd.DataFrame({
            "timestamp": [tweet["timestamp"] for tweet in tweets],
            "sentiment": [tweet["sentiment"] for tweet in tweets]
        })
        sentiment_df["timestamp"] = pd.to_datetime(sentiment_df["timestamp"])
        # Resample price data to match the number of tweets (simplified)
        price_df = price_df.iloc[:len(tweets)]
        combined_df = pd.concat([sentiment_df, price_df.reset_index(drop=True)], axis=1)
        correlation = combined_df["sentiment"].corr(combined_df["price"])
        log_message(f"Correlation coefficient: {correlation:.4f}")
        return combined_df, correlation

    def visualize_data(self, combined_df: pd.DataFrame) -> None:
        """
        Visualize sentiment scores and Bitcoin price trends.

        :param combined_df: A DataFrame with sentiment and price data.
        :return: None
        """
        log_message("Generating visualization of sentiment and price trends.")
        plt.figure(figsize=(10, 6))
        plt.plot(combined_df["timestamp"], combined_df["price"], label="Bitcoin Price (USD)", color="blue")
        plt.twinx()
        plt.plot(combined_df["timestamp"], combined_df["sentiment"], label="Sentiment Score", color="orange")
        plt.title("Bitcoin Price vs Sentiment Over Time")
        plt.legend()
        plt.savefig("sentiment_price_plot.png")
        log_message("Visualization saved to sentiment_price_plot.png.")
        plt.close()

    def run_analysis(self, keyword: str = "Bitcoin", max_tweets: int = 50) -> None:
        """
        Run the full sentiment analysis pipeline.

        :param keyword: The search term to query on Twitter (default: "Bitcoin").
        :param max_tweets: The maximum number of tweets to scrape (default: 50).
        :return: None
        """
        log_message("Starting Bitcoin sentiment analysis pipeline.")
        tweets = self.scrape_tweets(keyword, max_tweets)
        processed_tweets = self.preprocess_tweets(tweets)
        tweets_with_sentiment = self.analyze_sentiment(processed_tweets)
        price_df = self.fetch_bitcoin_price()
        combined_df, correlation = self.correlate_sentiment_price(tweets_with_sentiment, price_df)
        log_message(f"Correlation between sentiment and Bitcoin price: {correlation:.4f}")
        self.visualize_data(combined_df)
        log_message("Analysis pipeline completed.")

    def __del__(self):
        """
        Clean up resources when the object is deleted.

        :return: None
        """
        log_message("Closing Selenium WebDriver.")
        if hasattr(self, 'driver'):
            self.driver.quit()