"""
Scheduled Bitcoin Sentiment Analysis

This script handles both hourly and daily scheduled sentiment analysis
for Bitcoin news sources. It collects sentiment data at different frequencies:
- Hourly: Quick analysis of recent news (last few hours)
- Daily: Comprehensive analysis with larger data sample (past 24 hours)

The sentiment data is stored for use by the forecasting models.
"""

import os
import time
import datetime
import pandas as pd
import logging
import json
import argparse
from bitcoin_sentiment import BitcoinSentimentAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('sentiment_schedule.log')
    ]
)
logger = logging.getLogger('scheduled_sentiment')

# File paths for storing sentiment data
HOURLY_SENTIMENT_FILE = 'data/hourly_sentiment.csv'
DAILY_SENTIMENT_FILE = 'data/daily_sentiment.csv'
LATEST_SENTIMENT_FILE = 'data/latest_sentiment.json'

def ensure_data_directory():
    """Ensure the data directory exists."""
    os.makedirs('data', exist_ok=True)

def perform_hourly_analysis():
    """Perform hourly sentiment analysis on recent Bitcoin news."""
    logger.info("Starting hourly Bitcoin sentiment analysis...")
    
    try:
        analyzer = BitcoinSentimentAnalyzer()
        
        # Get sentiment from the past 24 hours with limited articles
        sentiment_df = analyzer.get_sentiment_dataframe(days=1, max_articles=15)
        
        if sentiment_df.empty:
            logger.warning("No sentiment data found in hourly analysis")
            return False
        
        # Save hourly results
        ensure_data_directory()
        
        # If file exists, append; otherwise create new
        if os.path.exists(HOURLY_SENTIMENT_FILE):
            existing_df = pd.read_csv(HOURLY_SENTIMENT_FILE, parse_dates=['date'])
            # Combine and remove duplicates by date
            combined_df = pd.concat([existing_df, sentiment_df]).drop_duplicates(subset=['date'])
            combined_df.to_csv(HOURLY_SENTIMENT_FILE, index=False)
        else:
            sentiment_df.to_csv(HOURLY_SENTIMENT_FILE, index=False)
        
        # Create summary for latest data
        latest_summary = analyzer.get_sentiment_summary(days=1, max_articles=15)
        
        # Save latest sentiment summary
        with open(LATEST_SENTIMENT_FILE, 'w') as f:
            json.dump(latest_summary, f, default=str)
        
        logger.info(f"Hourly analysis complete. Analyzed {len(sentiment_df)} records.")
        return True
        
    except Exception as e:
        logger.error(f"Error in hourly sentiment analysis: {str(e)}")
        return False

def perform_daily_analysis():
    """Perform comprehensive daily sentiment analysis."""
    logger.info("Starting daily Bitcoin sentiment analysis...")
    
    try:
        analyzer = BitcoinSentimentAnalyzer()
        
        # More comprehensive analysis with more articles and days
        sentiment_df = analyzer.get_sentiment_dataframe(days=7, max_articles=50)
        
        if sentiment_df.empty:
            logger.warning("No sentiment data found in daily analysis")
            return False
        
        # Save daily results
        ensure_data_directory()
        
        # If file exists, append; otherwise create new
        if os.path.exists(DAILY_SENTIMENT_FILE):
            existing_df = pd.read_csv(DAILY_SENTIMENT_FILE, parse_dates=['date'])
            # Combine and remove duplicates by date
            combined_df = pd.concat([existing_df, sentiment_df]).drop_duplicates(subset=['date'])
            combined_df.to_csv(DAILY_SENTIMENT_FILE, index=False)
        else:
            sentiment_df.to_csv(DAILY_SENTIMENT_FILE, index=False)
        
        logger.info(f"Daily analysis complete. Analyzed {len(sentiment_df)} records.")
        return True
        
    except Exception as e:
        logger.error(f"Error in daily sentiment analysis: {str(e)}")
        return False

def run_scheduled_analysis(mode='both', run_once=False):
    """
    Run sentiment analysis on a schedule.
    
    Args:
        mode: 'hourly', 'daily', or 'both'
        run_once: If True, run once and exit; otherwise run continuously
    """
    if run_once:
        if mode in ['hourly', 'both']:
            perform_hourly_analysis()
        if mode in ['daily', 'both']:
            perform_daily_analysis()
        return
    
    daily_last_run = None
    hourly_last_run = None
    
    logger.info(f"Starting scheduled sentiment analysis in {mode} mode")
    
    while True:
        now = datetime.datetime.now()
        
        # Daily analysis at 00:05 (to ensure we get full day)
        if mode in ['daily', 'both']:
            if daily_last_run is None or (now.day != daily_last_run.day):
                if now.hour == 0 and now.minute >= 5:
                    logger.info("Running scheduled daily analysis...")
                    perform_daily_analysis()
                    daily_last_run = now
        
        # Hourly analysis at the start of each hour
        if mode in ['hourly', 'both']:
            if hourly_last_run is None or (now - hourly_last_run).total_seconds() >= 3600:
                logger.info("Running scheduled hourly analysis...")
                perform_hourly_analysis()
                hourly_last_run = now
        
        # Sleep for a minute before checking again
        time.sleep(60)

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Scheduled Bitcoin Sentiment Analysis')
    parser.add_argument('--mode', choices=['hourly', 'daily', 'both'], default='both',
                       help='Analysis frequency mode')
    parser.add_argument('--run-once', action='store_true',
                       help='Run once and exit (no scheduling)')
    
    args = parser.parse_args()
    
    ensure_data_directory()
    run_scheduled_analysis(mode=args.mode, run_once=args.run_once)

if __name__ == "__main__":
    main()