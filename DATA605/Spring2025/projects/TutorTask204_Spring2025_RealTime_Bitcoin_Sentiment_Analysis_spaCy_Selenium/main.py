import logging
from Bitcoin_API import BitcoinSentimentAnalyzer

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_LOG = logging.getLogger(__name__)

def main():
    _LOG.info("Starting Bitcoin sentiment analysis.")
    analyzer = BitcoinSentimentAnalyzer()
    analyzer.run_analysis(keyword="Bitcoin", max_tweets=50)
    _LOG.info("Analysis completed.")

if __name__ == "__main__":
    main()