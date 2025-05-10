import os
import pandas as pd
import time
from fetch_news import fetch_bitcoin_news
from fetch_prices import fetch_bitcoin_prices
from extract_keywords import extract_keywords
from analyze_trends import analyze_trends
from visualize import plot_keyword_vs_price, plot_keyword_price_heatmap, generate_keyword_trend_dashboard, is_docker
from granger import run_granger_tests

def main():
    """
    Run the full Bitcoin news keyword trend analysis pipeline.
    """
    # Ensure all directories exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('figures', exist_ok=True)
    
    # Check if running in Docker
    running_in_docker = is_docker()
    
    print("🔍 Starting Bitcoin news keyword trend analysis...")
    
    try:
        # Step 1: Fetch news data
        print("\n📰 Fetching Bitcoin news articles...")
        news_data = fetch_bitcoin_news(days=30)  # Get 30 days of data for better analysis
        
        if news_data is None or len(news_data) == 0:
            print("⚠️ No news data retrieved. Using sample data for demonstration...")
            # Create sample data
            sample_data = {
                'title': ['Bitcoin hits new high', 'Crypto regulations coming', 'Market analysis'],
                'description': ['Bitcoin price surges', 'New regulations expected', 'Analysts predict growth'],
                'publishedAt': ['2023-05-01', '2023-05-02', '2023-05-03'],
                'source': ['CryptoNews', 'FinanceDaily', 'InvestorPost']
            }
            news_data = pd.DataFrame(sample_data)
            news_data['publishedAt'] = pd.to_datetime(news_data['publishedAt'])
            news_data['date'] = news_data['publishedAt'].dt.date
            news_data['hour'] = news_data['publishedAt'].dt.hour
            
            # Save the sample data
            news_data.to_csv('data/bitcoin_news.csv', index=False)
            print("✅ Sample news data created")
        
        # Step 2: Fetch price data
        print("\n💰 Fetching Bitcoin price data...")
        price_data = fetch_bitcoin_prices(days=30, interval='daily')
        
        if price_data is None:
            print("⚠️ No price data retrieved. Using sample data for demonstration...")
            # Create sample price data
            dates = pd.date_range(start='2023-05-01', periods=3)
            sample_prices = {
                'timestamp': dates,
                'price': [50000, 51000, 52000], 
                'date': [d.date() for d in dates],
                'hour': [0, 0, 0]
            }
            price_data = pd.DataFrame(sample_prices)
            
            # Save the sample data
            price_data.to_csv('data/bitcoin_prices.csv', index=False)
            print("✅ Sample price data created")
    
        # Step 3: Process data - extract keywords
        print("\n🔑 Extracting keywords from news articles...")
        news_with_keywords = extract_keywords(min_frequency=1, include_titles=True)
        
        # If keyword extraction failed, add basic keywords
        if news_with_keywords is None:
            print("⚠️ Keyword extraction failed. Creating basic keywords...")
            
            # Read the news data again
            if os.path.exists('data/bitcoin_news.csv'):
                news_data = pd.read_csv('data/bitcoin_news.csv')
                news_data['keywords'] = [['bitcoin', 'price'], ['regulation'], ['market', 'analysis']]
                
                # Save with basic keywords
                news_data.to_csv('data/bitcoin_news_with_keywords.csv', index=False)
                print("✅ Basic keywords added")
            else:
                print("❌ Cannot proceed without news data")
                return
        
        # Step 4: Analyze trends
        print("\n📊 Analyzing keyword trends and price correlations...")
        trend_data = analyze_trends(time_window='daily', min_freq=1)  # Lower threshold for min_freq
        
        if trend_data is None or trend_data.empty:
            print("❌ Trend analysis failed. Cannot proceed with visualization.")
            return
        
        # Small delay to make sure files are written
        time.sleep(1)
        
        # Step 5: Run Granger causality tests with appropriate parameters
        print("\n🧪 Running Granger causality tests...")
        
        # Check if we have enough data for meaningful Granger tests
        keyword_counts = trend_data.groupby('keyword').size()
        if keyword_counts.max() >= 10:
            # We have sufficient data for standard tests
            run_granger_tests(top_n=10, max_lag=3, min_data_points=10)
        elif keyword_counts.max() >= 5:
            # We have moderate data - use reduced parameters
            run_granger_tests(top_n=5, max_lag=1, min_data_points=5)
        else:
            # Limited data - use minimal parameters and show a warning
            print("⚠️ Limited data for causality testing. Using minimal parameters.")
            run_granger_tests(top_n=3, max_lag=1, min_data_points=3)
        
        # Step 6: Generate visualizations
        print("\n📊 Generating visualizations...")
        
        # Get top keywords - handle edge cases
        if 'keyword' in trend_data.columns:
            top_keywords = trend_data['keyword'].value_counts().head(3).index.tolist()
        else:
            print("⚠️ Missing keyword column in trend data. Using default keywords.")
            top_keywords = ['bitcoin', 'price', 'market']
        
        # Display correlation heatmap
        print("\n📊 Creating correlation heatmap...")
        plot_keyword_price_heatmap(
            top_n=min(5, len(top_keywords)),
            save_fig=True,  # Always save to file
            display_fig=not running_in_docker  # Only display if not in Docker
        )
        
        # Allow time between visualizations
        time.sleep(2)
        
        # Create individual keyword charts
        for keyword in top_keywords:
            print(f"\n📈 Creating visualization for keyword '{keyword}'...")
            plot_keyword_vs_price(
                keyword,
                save_fig=True,  # Always save to file
                display_fig=not running_in_docker  # Only display if not in Docker
            )
            # Allow time between visualizations
            time.sleep(2)
        
        print("\n✅ Analysis complete!")
        
        if running_in_docker:
            print("\n📊 Visualizations have been saved to the figures/ directory.")
            print("    Check the mounted directory on your host machine to view them.")
        else:
            print("\n📊 Visualizations have been displayed using matplotlib.")
        
    except Exception as e:
        print(f"\n❌ An error occurred during analysis: {str(e)}")
        print("Try running individual components manually for more detailed error messages.")

if __name__ == "__main__":
    main()
