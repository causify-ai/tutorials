"""
Sentiment Analysis Scheduler for Bitcoin Price Forecasting

This module provides functions to manage scheduled sentiment analysis
and access the collected sentiment data at different time frequencies.
"""

import os
import pandas as pd
import json
import logging
import subprocess
import threading
import time
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('sentiment_scheduler')

# Paths for sentiment data files created by the scheduler
HOURLY_SENTIMENT_FILE = 'data/hourly_sentiment.csv'
DAILY_SENTIMENT_FILE = 'data/daily_sentiment.csv'
LATEST_SENTIMENT_FILE = 'data/latest_sentiment.json'

class SentimentScheduler:
    """
    Class to manage Bitcoin sentiment analysis scheduling
    and provide access to collected sentiment data.
    """
    
    def __init__(self):
        """Initialize the sentiment scheduler."""
        self.hourly_thread = None
        self.daily_thread = None
        self.is_running = False
    
    def start_background_tasks(self):
        """Start background tasks for sentiment analysis."""
        if self.is_running:
            logger.info("Sentiment scheduler is already running.")
            return
        
        self.is_running = True
        
        # Start hourly sentiment analysis in background
        self.hourly_thread = threading.Thread(
            target=self._run_hourly_schedule,
            daemon=True
        )
        self.hourly_thread.start()
        
        # Start daily sentiment analysis in background
        self.daily_thread = threading.Thread(
            target=self._run_daily_schedule,
            daemon=True
        )
        self.daily_thread.start()
        
        logger.info("Sentiment scheduler started in background.")
    
    def _run_hourly_schedule(self):
        """Run hourly sentiment analysis on a schedule."""
        logger.info("Starting hourly sentiment scheduling...")
        
        # Run once immediately
        self._run_sentiment_analysis(mode='hourly')
        
        # Start scheduled runs
        last_run_hour = datetime.now().hour
        
        while self.is_running:
            now = datetime.now()
            
            # Run at the start of each hour
            if now.hour != last_run_hour:
                logger.info(f"Running scheduled hourly sentiment analysis at {now}")
                self._run_sentiment_analysis(mode='hourly')
                last_run_hour = now.hour
            
            # Sleep for 5 minutes before checking again
            time.sleep(300)
    
    def _run_daily_schedule(self):
        """Run daily sentiment analysis on a schedule."""
        logger.info("Starting daily sentiment scheduling...")
        
        # Run once immediately if no daily data exists
        if not os.path.exists(DAILY_SENTIMENT_FILE):
            self._run_sentiment_analysis(mode='daily')
        
        # Start scheduled runs
        last_run_day = datetime.now().day
        
        while self.is_running:
            now = datetime.now()
            
            # Run at midnight each day
            if now.day != last_run_day and now.hour == 0:
                logger.info(f"Running scheduled daily sentiment analysis at {now}")
                self._run_sentiment_analysis(mode='daily')
                last_run_day = now.day
            
            # Sleep for 15 minutes before checking again
            time.sleep(900)
    
    def _run_sentiment_analysis(self, mode='both'):
        """Run sentiment analysis using the scheduled script."""
        try:
            # Run the sentiment analysis script with the specified mode
            cmd = ['python', 'scheduled_sentiment_analysis.py', '--mode', mode, '--run-once']
            subprocess.run(cmd, check=True)
            logger.info(f"Successfully ran {mode} sentiment analysis")
            return True
        except Exception as e:
            logger.error(f"Error running {mode} sentiment analysis: {str(e)}")
            return False
    
    def get_latest_sentiment(self):
        """
        Get the latest sentiment data.
        
        Returns:
            dict: Dictionary with latest sentiment data or empty dict if not available
        """
        if os.path.exists(LATEST_SENTIMENT_FILE):
            try:
                with open(LATEST_SENTIMENT_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error reading latest sentiment data: {str(e)}")
        
        return {}
    
    def get_hourly_sentiment(self, days=1):
        """
        Get hourly sentiment data for the specified number of days.
        
        Args:
            days: Number of days of data to retrieve
            
        Returns:
            pd.DataFrame: DataFrame with hourly sentiment data
        """
        if os.path.exists(HOURLY_SENTIMENT_FILE):
            try:
                df = pd.read_csv(HOURLY_SENTIMENT_FILE, parse_dates=['date'])
                
                # Filter for the requested days
                if days > 0:
                    cutoff_date = datetime.now() - timedelta(days=days)
                    df = df[df['date'] >= cutoff_date]
                
                return df
            except Exception as e:
                logger.error(f"Error reading hourly sentiment data: {str(e)}")
        
        return pd.DataFrame()
    
    def get_daily_sentiment(self, days=7):
        """
        Get daily sentiment data for the specified number of days.
        
        Args:
            days: Number of days of data to retrieve
            
        Returns:
            pd.DataFrame: DataFrame with daily sentiment data
        """
        if os.path.exists(DAILY_SENTIMENT_FILE):
            try:
                df = pd.read_csv(DAILY_SENTIMENT_FILE, parse_dates=['date'])
                
                # Filter for the requested days
                if days > 0:
                    cutoff_date = datetime.now() - timedelta(days=days)
                    df = df[df['date'] >= cutoff_date]
                
                return df
            except Exception as e:
                logger.error(f"Error reading daily sentiment data: {str(e)}")
        
        return pd.DataFrame()
    
    def get_sentiment_for_forecasting(self, price_df, frequency='daily'):
        """
        Get sentiment data prepared for forecasting models.
        
        Args:
            price_df: DataFrame with price data
            frequency: 'hourly' or 'daily' sentiment data
            
        Returns:
            pd.DataFrame: Price DataFrame with added sentiment features
        """
        # Get sentiment data based on frequency
        if frequency == 'hourly':
            sentiment_df = self.get_hourly_sentiment()
        else:
            sentiment_df = self.get_daily_sentiment()
        
        if sentiment_df.empty or price_df.empty:
            return price_df
        
        try:
            # Create a new DataFrame with price data
            result_df = price_df.copy()
            
            # Add sentiment column
            result_df['sentiment_polarity'] = None
            
            # Map sentiment data to price data dates
            for date, row in sentiment_df.iterrows():
                date_str = pd.to_datetime(row['date']).strftime('%Y-%m-%d')
                
                for price_date in result_df.index:
                    price_date_str = price_date.strftime('%Y-%m-%d')
                    
                    if price_date_str == date_str:
                        result_df.at[price_date, 'sentiment_polarity'] = row['avg_polarity']
            
            # Fill missing values
            if 'sentiment_polarity' in result_df.columns:
                # Forward fill then backfill to ensure all dates have values
                result_df['sentiment_polarity'] = result_df['sentiment_polarity'].fillna(method='ffill').fillna(method='bfill')
                
                # Add lag features
                result_df['sentiment_polarity_lag1'] = result_df['sentiment_polarity'].shift(1).fillna(0)
                result_df['sentiment_polarity_lag2'] = result_df['sentiment_polarity'].shift(2).fillna(0)
                result_df['sentiment_momentum'] = result_df['sentiment_polarity'] - result_df['sentiment_polarity_lag1']
                
                return result_df
            
        except Exception as e:
            logger.error(f"Error creating sentiment features: {str(e)}")
        
        return price_df

# Create a global instance
scheduler = SentimentScheduler()

def start_sentiment_scheduling():
    """Start the sentiment scheduler in the background."""
    scheduler.start_background_tasks()

def get_sentiment_for_forecasting(price_df, frequency='daily'):
    """Get sentiment data for forecasting models."""
    return scheduler.get_sentiment_for_forecasting(price_df, frequency)

def get_latest_sentiment():
    """Get the latest sentiment data."""
    return scheduler.get_latest_sentiment()