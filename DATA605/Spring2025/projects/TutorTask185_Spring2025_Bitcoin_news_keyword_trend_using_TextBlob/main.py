import os
import pandas as pd
import time
import sys
import traceback
from datetime import datetime
from fetch_news import fetch_bitcoin_news
from fetch_prices import fetch_bitcoin_prices, fetch_current_bitcoin_price
from extract_keywords import extract_keywords
from analyze_trends import analyze_trends
from visualize import plot_keyword_vs_price, plot_keyword_price_heatmap, generate_keyword_trend_dashboard, is_docker
from granger import run_granger_tests

def print_header():
    """Print a nice header for the application."""
    print("")
    print("=" * 80)
    print("🔎 BITCOIN NEWS KEYWORD TREND ANALYSIS 🔎")
    print("=" * 80)
    print("Analyzing Bitcoin-related news to identify trending keywords")
    print("and correlate their frequency with Bitcoin price movements.")
    print("=" * 80)
    print("")

def ensure_directories():
    """Create necessary directories if they don't exist."""
    os.makedirs('data', exist_ok=True)
    os.makedirs('figures', exist_ok=True)
    os.makedirs('figures/html', exist_ok=True)
    os.makedirs('dashboard', exist_ok=True)
    
    # Clean up any existing trends overview files that are causing issues
    try:
        if os.path.exists('figures/keyword_trends_overview.png'):
            os.remove('figures/keyword_trends_overview.png')
            print("🧹 Removed old trends overview image")
            
        if os.path.exists('figures/html/keyword_trends_overview.html'):
            os.remove('figures/html/keyword_trends_overview.html')
            print("🧹 Removed old trends overview HTML")
            
        if os.path.exists('dashboard/assets/keyword_trends_overview.png'):
            os.remove('dashboard/assets/keyword_trends_overview.png')
            print("🧹 Removed old trends overview from dashboard assets")
    except Exception as cleanup_error:
        print(f"⚠️ Warning during cleanup: {str(cleanup_error)}")

def main():
    """
    Run the full Bitcoin news keyword trend analysis pipeline.
    """
    # Print header
    print_header()
    
    # Ensure all directories exist
    ensure_directories()
    
    # Check if running in Docker
    running_in_docker = is_docker()
    if running_in_docker:
        print("🐳 Running inside Docker container")
    
    try:
        # Fetch current Bitcoin price first (for dashboard)
        print("\n💰 Fetching current Bitcoin price...")
        current_price = fetch_current_bitcoin_price()
        if current_price:
            print(f"✅ Current Bitcoin price: ${current_price['price']:,.2f}")
        else:
            print("⚠️ Could not get current Bitcoin price. Dashboard will use historical or sample data.")
        
        # Step 1: Fetch news data
        print("\n📰 Fetching Bitcoin news articles...")
        news_data = fetch_bitcoin_news(days=30)  # Get 30 days of data for better analysis
        
        if news_data is None or len(news_data) == 0:
            print("⚠️ No news data retrieved. Using sample data for demonstration...")
            # Create sample data (this could happen if API key is not set or exceeded rate limits)
            sample_data = {
                'title': [
                    'Bitcoin hits new high as institutional investors pile in', 
                    'Crypto regulations coming soon, says Treasury Secretary',
                    'Bitcoin halving approaches, analysts predict price surge',
                    'Market analysis shows crypto adoption increasing globally',
                    'ETF approval speculation drives Bitcoin volatility'
                ],
                'description': [
                    'Bitcoin price surges past $60,000 as major hedge funds announce investments', 
                    'New regulations expected by end of quarter, crypto exchanges preparing for compliance',
                    'With the Bitcoin halving scheduled for April, analysts expect significant price movement',
                    'Research shows cryptocurrency adoption has increased 40% year-over-year',
                    'Market speculation about potential ETF approval has caused increased trading volume'
                ],
                'publishedAt': [
                    '2023-05-01T08:00:00Z', 
                    '2023-05-02T10:30:00Z', 
                    '2023-05-03T12:15:00Z',
                    '2023-05-04T14:45:00Z',
                    '2023-05-05T09:20:00Z'
                ],
                'source': ['CryptoNews', 'FinanceDaily', 'InvestorPost', 'BlockchainReport', 'CryptoAnalyst']
            }
            news_data = pd.DataFrame(sample_data)
            news_data['publishedAt'] = pd.to_datetime(news_data['publishedAt'])
            news_data['date'] = news_data['publishedAt'].dt.date
            news_data['hour'] = news_data['publishedAt'].dt.hour
            
            # Save the sample data
            news_data.to_csv('data/bitcoin_news.csv', index=False)
            print("✅ Sample news data created")
        else:
            print(f"✅ Successfully fetched {len(news_data)} news articles")
        
        # Step 2: Fetch price data
        print("\n💰 Fetching Bitcoin price data...")
        price_data = fetch_bitcoin_prices(days=30, interval='daily')
        
        if price_data is None:
            print("⚠️ No price data retrieved. Using sample data for demonstration...")
            # Create sample price data that mirrors actual Bitcoin behavior
            dates = pd.date_range(start='2023-05-01', periods=5)
            sample_prices = {
                'timestamp': dates,
                'price': [50000, 51200, 49800, 52300, 53100], 
                'date': [d.date() for d in dates],
                'hour': [0, 0, 0, 0, 0]
            }
            price_data = pd.DataFrame(sample_prices)
            
            # Save the sample data
            price_data.to_csv('data/bitcoin_prices.csv', index=False)
            print("✅ Sample price data created")
        else:
            print(f"✅ Successfully fetched {len(price_data)} price data points")
    
        # Step 3: Process data - extract keywords
        print("\n🔑 Extracting keywords from news articles...")
        news_with_keywords = extract_keywords(min_frequency=1, include_titles=True)
        
        # If keyword extraction failed, add basic keywords
        if news_with_keywords is None:
            print("⚠️ Keyword extraction failed. Creating basic keywords...")
            
            # Read the news data again
            if os.path.exists('data/bitcoin_news.csv'):
                news_data = pd.read_csv('data/bitcoin_news.csv')
                # Create more realistic but still synthetic keywords
                news_data['keywords'] = [
                    ['bitcoin', 'institutional', 'investors', 'price', 'surge'],
                    ['regulation', 'treasury', 'compliance', 'exchanges'],
                    ['halving', 'price', 'prediction', 'analysts'],
                    ['adoption', 'market', 'global', 'research'],
                    ['etf', 'approval', 'volatility', 'trading']
                ]
                
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
        print(f"📊 Found {len(keyword_counts)} unique keywords for causality testing")
        
        if keyword_counts.max() >= 10:
            # We have sufficient data for standard tests
            print("📊 Sufficient data available for standard causality tests")
            causality_results = run_granger_tests(top_n=10, max_lag=3, min_data_points=10)
        elif keyword_counts.max() >= 5:
            # We have moderate data - use reduced parameters
            print("📊 Moderate data available - using reduced test parameters")
            causality_results = run_granger_tests(top_n=5, max_lag=2, min_data_points=5)
        else:
            # Limited data - use minimal parameters and show a warning
            print("⚠️ Limited data for causality testing. Using minimal parameters.")
            causality_results = run_granger_tests(top_n=3, max_lag=1, min_data_points=3)
        
        # Step 6: Generate visualizations
        print("\n📊 Generating visualizations...")
        
        # Get top keywords - handle edge cases
        if 'keyword' in trend_data.columns:
            top_keywords = trend_data.nlargest(3, 'frequency')['keyword'].tolist()
            print(f"📊 Top keywords by frequency: {', '.join(top_keywords)}")
        else:
            print("⚠️ Missing keyword column in trend data. Using default keywords.")
            top_keywords = ['bitcoin', 'price', 'market']
        
        # Display correlation heatmap
        print("\n📊 Creating correlation heatmap...")
        plot_keyword_price_heatmap(
            top_n=min(5, len(trend_data)),
            save_fig=True,  # Always save to file
            display_fig=False  # Never display the figure
        )
        
        # Allow time between visualizations
        time.sleep(1)
        
        # Create individual keyword charts
        for keyword in top_keywords:
            print(f"\n📈 Creating visualization for keyword '{keyword}'...")
            plot_keyword_vs_price(
                keyword,
                save_fig=True,  # Always save to file
                display_fig=False  # Never display the figure
            )
            # Allow time between visualizations
            time.sleep(1)
        
        # Step 7: Generate dashboard
        print("\n📊 Generating interactive dashboard...")
        dashboard_path = generate_keyword_trend_dashboard()
        
        # Only open the dashboard
        if dashboard_path and not running_in_docker:
            try:
                print("\n🌐 Opening dashboard in browser...")
                # Use a single method to open the dashboard
                import webbrowser
                webbrowser.open(f'file:///{os.path.abspath(dashboard_path)}')
            except Exception as e:
                print(f"\n⚠️ Could not open dashboard automatically: {str(e)}")
                print(f"Please manually open the dashboard at: {os.path.abspath(dashboard_path)}")
        
        # Final message
        print("\n✅ Analysis complete!")
        print("\n📊 RESULTS SUMMARY 📊")
        print("=" * 40)
        print(f"📰 Analyzed {len(news_data)} news articles")
        print(f"🔑 Extracted {len(trend_data)} unique keywords")
        print(f"📈 Top keywords: {', '.join(top_keywords)}")
        
        # Show where to find results
        print("\n📁 OUTPUT FILES 📁")
        print("=" * 40)
        print("📊 Data files saved in: ./data/")
        print("📈 Visualizations saved in: ./figures/")
        
        if dashboard_path:
            print(f"🌐 Interactive dashboard: {dashboard_path}")
            
            if running_in_docker:
                print("\n📊 Visualizations have been saved to the figures/ directory.")
                print("    Check the mounted directory on your host machine to view them.")
            else:
                print("\n📊 Dashboard has been opened in your browser.")
        else:
            print("⚠️ Interactive dashboard could not be generated. Check individual visualizations.")
        
    except Exception as e:
        print(f"\n❌ An error occurred during analysis: {str(e)}")
        print("\nDetailed error information:")
        traceback.print_exc()
        print("\nTry running individual components manually for more detailed error messages.")

def check_environment():
    """Check if the environment is properly set up."""
    # Check for API key
    if not os.getenv('NEWSAPI_KEY'):
        print("\n\u26a0\ufe0f NewsAPI key not found in environment variables.")
        print("The program will run with sample data for demonstration purposes.")
        print("To use real data, set the NEWSAPI_KEY environment variable.")
        print("You can get an API key at: https://newsapi.org/")
        
        # Create .env.example if it doesn't exist
        if not os.path.exists('.env.example'):
            try:
                with open('.env.example', 'w') as f:
                    f.write("# Bitcoin News Keyword Trend Analysis - Environment Variables\n\n")
                    f.write("# NewsAPI - Get your key at https://newsapi.org/\n")
                    f.write("NEWSAPI_KEY=your_api_key_here\n\n")
                    f.write("# These settings can be configured as needed\n")
                    f.write("DEBUG_MODE=false\n")
                    f.write("FETCH_DAYS=30\n")
                print("\n\u2705 Created .env.example file as a template")
            except Exception as e:
                print(f"\u26a0\ufe0f Could not create .env.example: {str(e)}")
    else:
        print("\n\u2705 NewsAPI key found in environment")

if __name__ == "__main__":
    # Check environment before running
    check_environment()
    
    # Run the main pipeline
    main()
