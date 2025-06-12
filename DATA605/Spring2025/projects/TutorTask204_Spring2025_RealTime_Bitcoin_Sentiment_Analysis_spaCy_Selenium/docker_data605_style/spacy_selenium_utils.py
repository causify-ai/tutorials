"""
Utility module for the Bitcoin sentiment analysis project, including spaCy and Selenium functionality.

1. Citations:
   - Selenium Twitter scraping inspired by: https://github.com/selenium-twitter-scraper
   - VADER sentiment analysis: Hutto, C.J. & Gilbert, E.E. (2014). VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text.
   - CoinGecko API: https://www.coingecko.com/en/api/documentation
2. Run the linter on this script before committing changes to ensure consistency with the coding style.
3. Refer to spacy_API.md for detailed system documentation.

Follow the coding style guide: https://github.com/causify-ai/helpers/blob/master/docs/coding/all.coding_style.how_to_guide.md
"""

# Import libraries in this section.
import logging
import time
from typing import List, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import spacy
import re
from scipy.stats import spearmanr, kendalltau
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Set up logger for the module.
_LOG = logging.getLogger(__name__)

def log_message(message: str) -> None:
    """
    Log a message with INFO level.

    :param message: The message to log.
    :return: None
    """
    _LOG.info(message)

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
        # Initialize spaCy for NLP processing
        self.nlp = spacy.load("en_core_web_sm")
        # Initialize VADER for sentiment analysis
        self.sid = SentimentIntensityAnalyzer()
        # Fetch coin list from CoinGecko for entity matching
        url = "https://api.coingecko.com/api/v3/coins/list"
        try:
            response = requests.get(url)
            response.raise_for_status()
            coins = response.json()
            self.coin_list = [coin["name"].lower() for coin in coins]
        except requests.RequestException as e:
            log_message(f"Error fetching CoinGecko data: {str(e)}")
            self.coin_list = []
        # Store X credentials
        self.x_username = x_username
        self.x_password = x_password
        # Set up Selenium WebDriver in headless mode
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
            # Try multiple selectors for username field
            username_selectors = [
                (By.NAME, "text"),
                (By.CSS_SELECTOR, "input[autocomplete='username']"),
                (By.XPATH, "//input[@name='text' or @autocomplete='username']")
            ]
            username_field = None
            for by, selector in username_selectors:
                try:
                    username_field = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    break
                except TimeoutException:
                    continue

            if not username_field:
                raise TimeoutException("Username field not found with any selector.")

            username_field.send_keys(self.x_username)

            # Try multiple selectors for the Next button
            next_button_selectors = [
                (By.XPATH, "//span[contains(text(), 'Next')]"),
                (By.CSS_SELECTOR, "button[role='button'] span[contains(text(), 'Next')]"),
                (By.XPATH, "//button[@role='button' and .//span[contains(text(), 'Next')]]")
            ]
            next_button = None
            for by, selector in next_button_selectors:
                try:
                    next_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    break
                except TimeoutException:
                    continue

            if not next_button:
                raise TimeoutException("Next button not found with any selector.")

            # Retry clicking "Next" button up to 3 times
            retry_attempts = 3
            for attempt in range(retry_attempts):
                try:
                    next_button.click()
                    break
                except Exception as e:
                    log_message(f"Attempt {attempt + 1} to click Next button failed: {str(e)}")
                    if attempt == retry_attempts - 1:
                        raise TimeoutException("Failed to click Next button after retries.")
                    time.sleep(2)

            time.sleep(10)  # Increased delay to ensure password page loads

            # Check for intermediate verification prompts (e.g., email verification)
            try:
                verification_prompt = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Verify your email') or contains(text(), 'Verify your phone')]"))
                )
                log_message("Verification prompt detected (email/phone). Manual intervention required.")
                self.driver.save_screenshot("verification_prompt_screenshot.png")
                log_message("Screenshot saved as verification_prompt_screenshot.png")
                raise Exception("Verification prompt encountered. Please handle manually.")
            except TimeoutException:
                # No email/phone verification prompt detected, continue
                pass

            # Try multiple selectors for password field
            password_selectors = [
                (By.NAME, "password"),
                (By.CSS_SELECTOR, "input[autocomplete='current-password']"),
                (By.XPATH, "//input[@name='password' or @autocomplete='current-password']"),
                (By.CSS_SELECTOR, "input[type='password']"),
                (By.XPATH, "//input[@type='password']"),
                (By.CSS_SELECTOR, "input[data-testid='password']"),
                (By.XPATH, "//input[contains(@class, 'password')]")
            ]
            password_field = None
            for by, selector in password_selectors:
                try:
                    password_field = WebDriverWait(self.driver, 30).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    break
                except TimeoutException:
                    continue

            if not password_field:
                # Log the page source for debugging
                log_message("Password field not found. Current URL: " + self.driver.current_url)
                log_message("Page source snippet:")
                page_source = self.driver.page_source
                log_message(page_source[:1000])
                self.driver.save_screenshot("password_field_failure_screenshot.png")
                log_message("Screenshot saved as password_field_failure_screenshot.png")
                raise TimeoutException("Password field not found with any selector.")

            password_field.send_keys(self.x_password)

            # Try multiple selectors for the Log in button
            login_button_selectors = [
                (By.XPATH, "//span[contains(text(), 'Log in')]"),
                (By.CSS_SELECTOR, "button[role='button'] span[contains(text(), 'Log in')]"),
                (By.XPATH, "//button[@role='button' and .//span[contains(text(), 'Log in')]]"),
                (By.CSS_SELECTOR, "button[data-testid='LoginForm_Login_Button']")
            ]
            login_button = None
            for by, selector in login_button_selectors:
                try:
                    login_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    break
                except TimeoutException:
                    continue

            if not login_button:
                raise TimeoutException("Log in button not found with any selector.")

            login_button.click()
            time.sleep(5)  # Wait for login to complete

            # Check for 2FA or verification prompts
            try:
                verification_prompt = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name='verification_code']"))
                )
                log_message("2FA or verification prompt detected. Manual intervention required.")
                self.driver.save_screenshot("2fa_verification_screenshot.png")
                log_message("Screenshot saved as 2fa_verification_screenshot.png")
                raise Exception("2FA or verification prompt encountered. Please handle manually.")
            except TimeoutException:
                # No 2FA prompt detected, continue
                pass

            log_message("Successfully logged in to X.")
        except Exception as e:
            log_message(f"Failed to log in to X: {str(e)}")
            self.driver.save_screenshot("login_failure_screenshot.png")
            log_message("Screenshot of login failure saved as login_failure_screenshot.png")
            raise

    def scrape_tweets(self, keywords: List[str], max_tweets: int) -> List[dict]:
        """
        Scrape tweets containing the specified keywords using Selenium.

        :param keywords: List of search terms to query on Twitter (e.g., ["Bitcoin", "BTC"]).
        :param max_tweets: The maximum number of tweets to scrape.
        :return: A list of dictionaries with tweet text and timestamp.
        """
        # Log in to X if credentials are provided
        self.login_to_x()

        all_tweets = []
        seen_texts = set()  # To track unique tweets and avoid duplicates

        for keyword in keywords:
            log_message(f"Scraping tweets for keyword: {keyword}")
            self.driver.get(f"https://x.com/search?q={keyword}&src=typed_query&f=live")
            time.sleep(5)  # Wait for initial page load

            tweets = []
            scroll_attempts = 0
            max_scroll_attempts = 50  # Limit to avoid infinite scrolling

            while len(tweets) < max_tweets and scroll_attempts < max_scroll_attempts:
                try:
                    # Try multiple selectors for tweet elements
                    tweet_selectors = [
                        (By.CSS_SELECTOR, 'article[data-testid="tweet"]'),
                        (By.CSS_SELECTOR, 'article[data-testid="post"]'),
                        (By.CSS_SELECTOR, 'div[data-testid="tweetText"]')
                    ]
                    tweet_elements = None
                    for by, selector in tweet_selectors:
                        try:
                            WebDriverWait(self.driver, 60).until(
                                EC.presence_of_element_located((by, selector))
                            )
                            if selector == 'div[data-testid="tweetText"]':
                                # If using tweetText, the parent article element is needed for context
                                tweet_elements = self.driver.find_elements(By.CSS_SELECTOR, 'article')
                            else:
                                tweet_elements = self.driver.find_elements(by, selector)
                            break
                        except TimeoutException:
                            continue

                    if not tweet_elements:
                        raise TimeoutException("Tweet elements not found with any selector.")

                    for element in tweet_elements:
                        try:
                            # Adjust text extraction based on selector
                            if 'tweetText' in selector:
                                text = element.find_element(By.CSS_SELECTOR, 'div[data-testid="tweetText"]').text
                            else:
                                text = element.find_element(By.CSS_SELECTOR, 'div[lang]').text
                            if text not in seen_texts:  # Check for duplicates
                                timestamp = pd.Timestamp.now().isoformat()
                                tweets.append({"text": text, "timestamp": timestamp})
                                seen_texts.add(text)
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

            log_message(f"Scraped {len(tweets)} tweets for keyword: {keyword}")
            all_tweets.extend(tweets)

        # Sort tweets by timestamp and limit to max_tweets
        all_tweets.sort(key=lambda x: x["timestamp"])
        all_tweets = all_tweets[:max_tweets]
        log_message(f"Total unique tweets after combining: {len(all_tweets)}")
        return all_tweets

    def preprocess_tweets(self, tweets: List[dict]) -> List[dict]:
        """
        Preprocess tweets using spaCy for tokenization, lemmatization, and cleaning.

        :param tweets: A list of tweet dictionaries with text and timestamp.
        :return: A list of preprocessed tweet dictionaries with entities.
        """
        log_message(f"Preprocessing {len(tweets)} tweets.")
        processed_tweets = []
        for tweet in tweets:
            # Inline clean_text logic
            cleaned_text = re.sub(r"http\S+|www\S+|https\S+", "", tweet["text"], flags=re.MULTILINE)
            cleaned_text = re.sub(r"@\w+|#\w+", "", cleaned_text)
            cleaned_text = cleaned_text.encode("ascii", "ignore").decode()  # Remove emojis
            cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
            
            # Inline extract_entities logic
            doc = self.nlp(cleaned_text)
            tokens = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct]
            processed_text = " ".join(tokens)
            entities = [(ent.text, ent.label_) for ent in doc.ents]
            
            # Inline match_entities_with_coins logic
            matched_coins = []
            for text, label in entities:
                if label in ["ORG", "PRODUCT", "PERSON"] and text.lower() in self.coin_list:
                    matched_coins.append(text)
                    
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

    def correlate_sentiment_price(self, tweets: List[dict], price_df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
        """
        Correlate sentiment scores with Bitcoin price data using multiple methods.

        :param tweets: A list of tweet dictionaries with sentiment scores.
        :param price_df: A DataFrame with Bitcoin price data.
        :return: A tuple containing the combined DataFrame and a dictionary of correlation coefficients.
        """
        log_message("Correlating sentiment with Bitcoin price.")
        sentiment_df = pd.DataFrame({
            "timestamp": [tweet["timestamp"] for tweet in tweets],
            "sentiment": [tweet["sentiment"] for tweet in tweets]
        })
        sentiment_df["timestamp"] = pd.to_datetime(sentiment_df["timestamp"])
        # Resample price data to match the number of tweets (simplified)
        price_df = price_df.iloc[:len(tweets)]
        # Rename timestamp column in price_df to avoid conflict
        price_df = price_df.rename(columns={"timestamp": "price_timestamp"})
        combined_df = pd.concat([sentiment_df, price_df.reset_index(drop=True)], axis=1)

        # Calculate additional metrics
        combined_df["price_change"] = combined_df["price"].pct_change()
        combined_df["cumulative_sentiment"] = combined_df["sentiment"].cumsum()

        # Calculate multiple correlation coefficients
        correlations = {}
        # Pearson correlation (linear)
        correlations["pearson"] = combined_df["sentiment"].corr(combined_df["price"])
        # Spearman correlation (monotonic)
        spearman_corr, _ = spearmanr(combined_df["sentiment"], combined_df["price"])
        correlations["spearman"] = spearman_corr
        # Kendall correlation (rank-based)
        kendall_corr, _ = kendalltau(combined_df["sentiment"], combined_df["price"])
        correlations["kendall"] = kendall_corr

        # Lagged correlation (shift sentiment by 1 to see if past sentiment predicts price)
        combined_df["sentiment_lagged"] = combined_df["sentiment"].shift(1)
        correlations["lagged_pearson"] = combined_df["sentiment_lagged"].corr(combined_df["price"])

        # Rolling correlation (window of 5)
        rolling_corr = combined_df["sentiment"].rolling(window=5).corr(combined_df["price"]).fillna(0)
        combined_df["rolling_corr"] = rolling_corr

        log_message("Correlation coefficients:")
        for method, value in correlations.items():
            log_message(f"{method.capitalize()}: {value:.4f}")

        return combined_df, correlations

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
        plt.show()
        plt.close()

    def visualize_sentiment_distribution_box(self, combined_df: pd.DataFrame) -> None:
        """
        Visualize the distribution of sentiment scores as a box plot.

        :param combined_df: A DataFrame with sentiment data.
        :return: None
        """
        log_message("Generating box plot of sentiment distribution.")
        plt.figure(figsize=(8, 6))
        plt.boxplot(combined_df["sentiment"], vert=False)
        plt.title("Distribution of Sentiment Scores")
        plt.xlabel("Sentiment Score")
        plt.show()
        plt.close()

    def visualize_cumulative_sentiment_area(self, combined_df: pd.DataFrame) -> None:
        """
        Visualize cumulative sentiment and Bitcoin price as an area plot.

        :param combined_df: A DataFrame with sentiment and price data.
        :return: None
        """
        log_message("Generating area plot of cumulative sentiment and price.")
        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax1.fill_between(combined_df["timestamp"], combined_df["cumulative_sentiment"], color="orange", alpha=0.3, label="Cumulative Sentiment")
        ax1.set_xlabel("Time")
        ax1.set_ylabel("Cumulative Sentiment", color="orange")
        ax1.tick_params(axis="y", labelcolor="orange")
        ax2 = ax1.twinx()
        ax2.plot(combined_df["timestamp"], combined_df["price"], color="blue", label="Bitcoin Price (USD)")
        ax2.set_ylabel("Bitcoin Price (USD)", color="blue")
        ax2.tick_params(axis="y", labelcolor="blue")
        fig.suptitle("Cumulative Sentiment vs Bitcoin Price")
        fig.legend(loc="upper right")
        plt.show()
        plt.close()

    def visualize_correlation_heatmap(self, combined_df: pd.DataFrame) -> None:
        """
        Visualize a heatmap of correlations between sentiment, price, and other metrics.

        :param combined_df: A DataFrame with sentiment and price data.
        :return: None
        """
        log_message("Generating correlation heatmap.")
        corr_matrix = combined_df[["sentiment", "price", "price_change", "rolling_corr"]].corr()
        plt.figure(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", vmin=-1, vmax=1)
        plt.title("Correlation Heatmap")
        plt.show()
        plt.close()

    def visualize_rolling_correlation(self, combined_df: pd.DataFrame) -> None:
        """
        Visualize the rolling correlation between sentiment and price over time.

        :param combined_df: A DataFrame with sentiment and price data.
        :return: None
        """
        log_message("Generating rolling correlation plot.")
        plt.figure(figsize=(10, 6))
        plt.plot(combined_df["timestamp"], combined_df["rolling_corr"], label="Rolling Correlation (window=5)", color="purple")
        plt.title("Rolling Correlation Between Sentiment and Bitcoin Price")
        plt.xlabel("Time")
        plt.ylabel("Correlation Coefficient")
        plt.legend()
        plt.show()
        plt.close()

    def run_analysis(self, keywords: List[str] = ["Bitcoin", "BTC"], max_tweets: int = 50) -> None:
        """
        Run the full sentiment analysis pipeline.

        :param keywords: List of search terms to query on Twitter (default: ["Bitcoin", "BTC"]).
        :param max_tweets: The maximum number of tweets to scrape (default: 50).
        :return: None
        """
        log_message("Starting Bitcoin sentiment analysis pipeline.")
        tweets = self.scrape_tweets(keywords, max_tweets)
        processed_tweets = self.preprocess_tweets(tweets)
        tweets_with_sentiment = self.analyze_sentiment(processed_tweets)
        price_df = self.fetch_bitcoin_price()
        combined_df, correlations = self.correlate_sentiment_price(tweets_with_sentiment, price_df)

        # Visualizations
        self.visualize_data(combined_df)
        self.visualize_sentiment_distribution_box(combined_df)
        self.visualize_cumulative_sentiment_area(combined_df)
        self.visualize_correlation_heatmap(combined_df)
        self.visualize_rolling_correlation(combined_df)

        log_message("Analysis pipeline completed.")

    def __del__(self):
        """
        Clean up resources when the object is deleted.

        :return: None
        """
        log_message("Closing Selenium WebDriver.")
        if hasattr(self, 'driver'):
            self.driver.quit()


def main() -> None:
    """
    Execute the main Bitcoin sentiment analysis pipeline.

    :return: None
    """
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    log_message("Starting main function.")
    analyzer = BitcoinSentimentAnalyzer(
        chromedriver_path="path/to/chromedriver",
        x_username="your_username",  # Replace with your X username
        x_password="your_password"   # Replace with your X password
    )
    analyzer.run_analysis(keywords=["Bitcoin", "BTC"], max_tweets=50)
    log_message("Main function completed.")


if __name__ == "__main__":
    main()