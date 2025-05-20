#!/usr/bin/env python3
"""
Bitcoin News Sentiment Analysis
-------------------------------
This script fetches recent Bitcoin news and analyzes sentiment using LLM.
"""

from bitcoin_utils import (
    Config, 
    fetch_bitcoin_news,
    process_news_articles,
    make_clickable,
    create_sentiment_pie_chart
)

import pandas as pd
import argparse
from datetime import datetime, timedelta
from IPython.display import HTML
import schedule
import time


def main():
    """Run the full Bitcoin news sentiment analysis pipeline."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Bitcoin News Sentiment Analysis")
    parser.add_argument("--days", type=int, default=1, 
                        help="Number of days to look back (default: 1)")
    parser.add_argument("--week", action="store_true", 
                        help="Fetch articles from the previous week")
    parser.add_argument("--from-date", type=str, 
                        help="Start date in YYYY-MM-DD format")
    parser.add_argument("--to-date", type=str, 
                        help="End date in YYYY-MM-DD format")
    parser.add_argument("--page-size", type=int, default=10, 
                        help="Number of articles to fetch (default: 10)")
    parser.add_argument("--provider", type=str, help="LLM provider to use (together_ai, openai, huggingface, gemini, ollama)")
    parser.add_argument("--loop", action="store_true", help="Run continuously on schedule")
    parser.add_argument("--interval", type=int, default=60,
                       help="Minutes between runs when using --loop (default: 60)")
    args = parser.parse_args()
    
    # Calculate date range
    if args.week:
        days_back = 7
    else:
        days_back = args.days
    
    print("Bitcoin News Sentiment Analysis")
    print("===============================")
    
    # Load configuration
    config = Config.load()
    # Set provider from argument if given
    if args.provider:
        config.PROVIDER = args.provider
    print(f"Using provider: {config.PROVIDER}")
    
    def run_analysis():
        """Run a single analysis cycle."""
        print(f"\nRunning sentiment analysis at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    # Process articles with date range
    print("\nFetching and analyzing Bitcoin news...")
    df = process_news_articles(
        config, 
        page_size=args.page_size, 
        days_back=days_back,
        custom_from_date=args.from_date,
        custom_to_date=args.to_date
    )
    
    # Display results
    if df.empty:
        print("No articles found or analyzed.")
        return
    
    print("\nSummary Statistics:")
    print(f"Total articles analyzed: {len(df)}")
    sentiment_counts = df['sentiment'].value_counts()
    for sentiment, count in sentiment_counts.items():
        print(f"  {sentiment}: {count} articles ({count/len(df)*100:.1f}%)")
    
    # Save results to data folder
    config.DATA_DIR.mkdir(exist_ok=True)  # Ensure data directory exists
    output_file = config.DATA_DIR / "bitcoin_sentiment_results.csv"
    df.to_csv(output_file, index=False)
    print(f"\nResults saved to {output_file}")
    
    if args.loop:
        print(f"Starting continuous analysis every {args.interval} minutes...")
        # Run immediately on startup
        run_analysis()
        
        # Schedule the job
        schedule.every(args.interval).minutes.do(run_analysis)
        
        # Keep the script running
        while True:
            schedule.run_pending()
            time.sleep(1)
    else:
        # Run once
        run_analysis()
    print("\nDone! You can now view the results in the data folder.")


if __name__ == "__main__":
    main()
