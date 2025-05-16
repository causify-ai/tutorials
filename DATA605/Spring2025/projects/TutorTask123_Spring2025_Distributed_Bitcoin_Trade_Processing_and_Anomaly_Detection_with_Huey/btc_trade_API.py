"""
btc_trade_API.py

Bitcoin Trade Processing Native API.

This module defines the core functions for:
- Monitoring Bitcoin trade data.
- Aggregating 1-min and 5-min OHLC metrics.
- Detecting anomalies using 3-sigma rule.
- Correlating trades with Reddit sentiment analysis.
- Sending Slack alerts on critical failures.

Reference:
- See btc_trade_API.md for detailed documentation.
"""

import os
import nltk
nltk.download('vader_lexicon')

import logging
import requests
from dotenv import load_dotenv
from huey import RedisHuey
from btc_trade_utils import huey

from prometheus_client import start_http_server, Counter, Summary
from btc_trade_utils import compute_ohlc, get_bucket, ohlc_1min, ohlc_5min
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import praw

# -----------------------------------------------------------------------------
# Setup Logging
# -----------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
_LOG = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Load Environment Variables
# -----------------------------------------------------------------------------

load_dotenv()
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

# -----------------------------------------------------------------------------
# Initialize Prometheus Metrics
# -----------------------------------------------------------------------------

TOTAL_TRADES = Counter("total_trades_processed", "Total number of trades processed")
ANOMALIES = Counter("anomalies_detected", "Number of anomalous trades detected")
TASK_DURATION = Summary("task_processing_seconds", "Time spent processing trades")

# -----------------------------------------------------------------------------
# Initialize Huey
# -----------------------------------------------------------------------------

#huey = RedisHuey('btc-trade', host='redis', port=6379)



# -----------------------------------------------------------------------------
# Utility Functions
# -----------------------------------------------------------------------------

def start_monitoring(port: int = 8000) -> None:
    """
    Start Prometheus HTTP server for monitoring.

    :param port: Port number for Prometheus server.
    """
    _LOG.info("Starting Prometheus server at port %s", port)
    start_http_server(port)


def send_slack_alert(message: str) -> None:
    """
    Send a Slack alert with a given message.

    :param message: Message to send.
    """
    if SLACK_WEBHOOK:
        try:
            response = requests.post(SLACK_WEBHOOK, json={"text": message})
            if response.status_code != 200:
                _LOG.error("Slack alert failed: %s", response.text)
        except Exception as e:
            _LOG.error("Slack alert error: %s", e)

# -----------------------------------------------------------------------------
# Core Huey Tasks
# -----------------------------------------------------------------------------

@huey.task()
def aggregate_trade(trade: dict) -> None:
    """
    Aggregate a trade into 1-min and 5-min OHLC metrics.

    :param trade: Trade data with 'price' and 'time'.
    """
    try:
        ts = trade["time"]
        price = float(trade["price"])

        bucket_1m = get_bucket(ts, '1min')
        bucket_5min = get_bucket(ts, '5min')

        ohlc_1min[bucket_1m].append(price)
        ohlc_5min[bucket_5min].append(price)

        _LOG.info("1-min OHLC: %s", compute_ohlc(ohlc_1min[bucket_1m]))
        _LOG.info("5-min OHLC: %s", compute_ohlc(ohlc_5min[bucket_5min]))

    except Exception as e:
        _LOG.error("Aggregation error: %s", e)


@huey.task(retries=3, retry_delay=10, retry_backoff=True)
def check_anomaly(trade_data: dict) -> None:
    """
    Check for anomalous trades (3-sigma rule).

    :param trade_data: Trade data dictionary.
    """
    price = trade_data.get("price")
    from anomaly import is_anomalous  
    if is_anomalous(price):
        ANOMALIES.inc()
        send_slack_alert(f"🚨 Anomalous trade: ${price}\nIt is 3σ outside the normal range.")


@huey.task(retries=3, retry_delay=5, retry_backoff=True)
def correlate_reddit_sentiment(trade_data: dict) -> None:
    """
    Correlate trades with Reddit Bitcoin sentiment.

    :param trade_data: Trade data dictionary.
    """
    try:
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
        vader = SentimentIntensityAnalyzer()

        posts = reddit.subreddit("Bitcoin").new(limit=10)
        sentiments = {"positive": 0, "negative": 0, "neutral": 0}

        for post in posts:
            score = vader.polarity_scores(post.title)["compound"]
            if score >= 0.05:
                sentiments["positive"] += 1
            elif score <= -0.05:
                sentiments["negative"] += 1
            else:
                sentiments["neutral"] += 1

        _LOG.info("🧠 Reddit Sentiment: %s", sentiments)

    except Exception as e:
        _LOG.error("Reddit sentiment failed: %s", e)


@huey.task()
@TASK_DURATION.time()
def process_trade(trade_data: dict) -> None:
    """
    Main task to process a trade (aggregation + anomaly check + sentiment).

    :param trade_data: Trade data dictionary.
    """
    TOTAL_TRADES.inc()
    aggregate_trade(trade_data)
    check_anomaly(trade_data)
    correlate_reddit_sentiment(trade_data)
