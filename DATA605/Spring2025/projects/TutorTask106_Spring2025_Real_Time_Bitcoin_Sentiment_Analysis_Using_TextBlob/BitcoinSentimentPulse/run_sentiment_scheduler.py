"""
Sentiment Scheduler Runner

This script starts the Bitcoin sentiment analysis scheduler
to run hourly and daily sentiment analysis in the background.
"""

import logging
import time
from sentiment_scheduler import start_sentiment_scheduling

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('sentiment_scheduler.log')
    ]
)

logger = logging.getLogger('sentiment_runner')

def main():
    """Start the sentiment scheduler and keep the script running."""
    logger.info("Starting Bitcoin sentiment analysis scheduler...")
    
    # Start the sentiment scheduler
    start_sentiment_scheduling()
    
    logger.info("Sentiment scheduler started. Press Ctrl+C to stop.")
    
    # Keep the script running
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Sentiment scheduler runner stopped by user.")

if __name__ == "__main__":
    main()