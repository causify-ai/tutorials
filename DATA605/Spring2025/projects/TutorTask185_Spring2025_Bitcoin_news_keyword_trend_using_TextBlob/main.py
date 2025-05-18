import os
import pandas as pd
import time
import sys
import traceback
import json
from datetime import datetime
# Replace individual imports with single import from TextBlob1_Utils
import TextBlob1_Utils as utils

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
    os.makedirs('dashboard/assets', exist_ok=True)
    
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

def generate_dashboard(top_keywords, trend_df, granger_results=None, current_price=None):
    """
    Generate an interactive dashboard with keyword trends and Bitcoin price data.
    
    Args:
        top_keywords (list): List of selected keywords for visualization
        trend_df (DataFrame): DataFrame with keyword trend data
        granger_results (DataFrame): Optional DataFrame with Granger causality results
        current_price (dict): Optional dictionary with current price data
        
    Returns:
        str: Path to the dashboard HTML file or None if error
    """
    try:
        # Check for required files
        if not os.path.exists('data/merged_keyword_price.csv'):
            print("❌ No merged keyword and price data found. Please run analyze_trends() first.")
            return None
            
        print("📊 Generating interactive dashboard...")
        
        # Load merged data
        merged_df = pd.read_csv('data/merged_keyword_price.csv')
        
        # Convert time column if needed
        if 'time_window' in merged_df.columns:
            merged_df['time_window'] = pd.to_datetime(merged_df['time_window'])
        
        # Get significant keywords from Granger causality results
        granger_significant = []
        if granger_results is not None and 'k2p_significant' in granger_results.columns:
            granger_significant = granger_results[granger_results['k2p_significant']]['keyword'].tolist()
        
        # Get current price data if available
        current_price_text = "N/A"
        current_price_change = "0"
        current_price_change_class = "neutral"
        
        if current_price and 'price' in current_price:
            current_price_text = f"${current_price['price']:,.2f}"
            if 'change_24h' in current_price:
                change = current_price['change_24h']
                current_price_change = f"{change:.2f}%"
                current_price_change_class = "positive" if change >= 0 else "negative"
        else:
            # Try to load from file if available
            if os.path.exists('data/current_price.json'):
                try:
                    with open('data/current_price.json', 'r') as f:
                        current_price = json.load(f)
                    if 'price' in current_price:
                        current_price_text = f"${current_price['price']:,.2f}"
                        if 'change_24h' in current_price:
                            change = current_price['change_24h']
                            current_price_change = f"{change:.2f}%"
                            current_price_change_class = "positive" if change >= 0 else "negative"
                except Exception as e:
                    print(f"⚠️ Error loading current price data: {str(e)}")
        
        # Create dashboard HTML file with enhanced layout and current price display
        dashboard_html = f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Bitcoin News Keyword Trends</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f5f5f5;
                    color: #333;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                header {{
                    background-color: #f2a900;
                    color: #fff;
                    padding: 20px 0;
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 5px solid #4d4d4d;
                    position: relative;
                }}
                h1 {{
                    margin: 0;
                    font-size: 28px;
                }}
                .dashboard-section {{
                    background-color: white;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    padding: 20px;
                    margin-bottom: 30px;
                }}
                h2 {{
                    color: #f2a900;
                    border-bottom: 2px solid #eee;
                    padding-bottom: 10px;
                    margin-top: 0;
                }}
                .iframe-container {{
                    position: relative;
                    overflow: hidden;
                    width: 100%;
                    padding-top: 56.25%; /* 16:9 Aspect Ratio */
                    margin: 20px 0;
                }}
                .iframe-container iframe {{
                    position: absolute;
                    top: 0;
                    left: 0;
                    bottom: 0;
                    right: 0;
                    width: 100%;
                    height: 100%;
                    border: none;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #777;
                    font-size: 12px;
                    margin-top: 50px;
                }}
                .keyword-tabs {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 5px;
                    margin: 20px 0;
                    border-bottom: 2px solid #f2a900;
                    padding-bottom: 10px;
                }}
                .keyword-tab {{
                    background-color: #e7e7e7;
                    color: #333;
                    border: none;
                    padding: 10px 15px;
                    border-radius: 5px 5px 0 0;
                    cursor: pointer;
                    font-weight: bold;
                    transition: background-color 0.3s;
                }}
                .keyword-tab:hover {{
                    background-color: #d4d4d4;
                }}
                .keyword-tab.active {{
                    background-color: #f2a900;
                    color: white;
                }}
                .tab-content {{
                    display: none;
                }}
                .tab-content.active {{
                    display: block;
                }}
                .chart-container {{
                    height: 400px;
                    margin: 20px 0;
                }}
                .current-price-box {{
                    position: absolute;
                    top: 20px;
                    right: 20px;
                    background-color: rgba(255, 255, 255, 0.9);
                    border-radius: 5px;
                    padding: 10px 15px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                    text-align: right;
                    color: #333;
                }}
                .price-label {{
                    font-size: 14px;
                    margin-bottom: 5px;
                    color: #555;
                }}
                .price-value {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #333;
                    margin-bottom: 5px;
                }}
                .price-change {{
                    font-size: 14px;
                    font-weight: bold;
                }}
                .positive {{
                    color: green;
                }}
                .negative {{
                    color: red;
                }}
                .neutral {{
                    color: gray;
                }}
                .granger-container {{
                    display: flex;
                    justify-content: center;
                    margin: 20px 0;
                }}
                .granger-container img {{
                    max-width: 100%;
                    height: auto;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                .granger-info {{
                    background-color: #f9f9f9;
                    border-left: 4px solid #f2a900;
                    padding: 10px 15px;
                    margin: 15px 0;
                    border-radius: 0 4px 4px 0;
                }}
                .significant-keyword {{
                    background-color: #f2a900;
                    color: white;
                    border-radius: 3px;
                    padding: 2px 5px;
                    margin: 0 3px;
                    font-weight: bold;
                }}
                @media (max-width: 768px) {{
                    .container {{
                        padding: 10px;
                    }}
                    h1 {{
                        font-size: 24px;
                    }}
                    .dashboard-section {{
                        padding: 15px;
                    }}
                    .chart-container {{
                        height: 300px;
                    }}
                    .current-price-box {{
                        position: relative;
                        top: 0;
                        right: 0;
                        margin: 10px auto;
                        text-align: center;
                    }}
                }}
            </style>
        </head>
        <body>
            <header>
                <h1>🔍 Bitcoin News Keyword Trends Analysis</h1>
                <p>Exploring relationships between news keywords and Bitcoin price</p>
                
                <div class="current-price-box">
                    <div class="price-label">Current Bitcoin Price:</div>
                    <div class="price-value">{current_price_text}</div>
                    <div class="price-change {current_price_change_class}">{current_price_change}</div>
                </div>
            </header>
            
            <div class="container">
                <div class="dashboard-section">
                    <h2>Keyword Correlation with Bitcoin Price</h2>
                    <p>This visualization shows how strongly different keywords are correlated with Bitcoin price movements.</p>
                    <div class="iframe-container">
                        <iframe src="../figures/html/keyword_correlation_interactive.html" frameborder="0"></iframe>
                    </div>
                </div>
        '''
        
        # Add Granger Causality section if the visualization exists
        if os.path.exists('figures/granger_causality_tests.png'):
            significant_keywords_html = ""
            if granger_significant:
                significant_keywords_html = "Significant keywords: " + " ".join([f'<span class="significant-keyword">{k}</span>' for k in granger_significant])
            
            dashboard_html += f'''
                <div class="dashboard-section">
                    <h2>Granger Causality Analysis</h2>
                    <p>This analysis shows which keywords might have predictive power for Bitcoin price movements.</p>
                    
                    <div class="granger-info">
                        <p><strong>What is Granger Causality?</strong> Granger causality tests whether past values of one variable (keyword frequency) 
                        can predict future values of another variable (Bitcoin price). A small p-value (&lt; 0.05) indicates a significant predictive relationship.</p>
                        {significant_keywords_html}
                    </div>
                    
                    <div class="granger-container">
                        <img src="../figures/granger_causality_tests.png" alt="Granger Causality Test Results">
                    </div>
                </div>
            '''
        
        dashboard_html += '''
                <div class="dashboard-section">
                    <h2>Keyword Trends over Time</h2>
                    <p>Select a keyword to see how its frequency in news relates to Bitcoin price:</p>
                    
                    <div class="keyword-tabs">
        '''
        
        # Add tabs for each top keyword
        for i, keyword in enumerate(top_keywords):
            active_class = "active" if i == 0 else ""
            dashboard_html += f'<button class="keyword-tab {active_class}" onclick="openTab(event, \'{keyword}\')">{keyword}</button>\n'
        
        dashboard_html += '''
                    </div>
        '''
        
        # Add tab content for each keyword
        for i, keyword in enumerate(top_keywords):
            safe_filename = utils.sanitize_filename(keyword)
            active_class = "active" if i == 0 else ""
            dashboard_html += f'''
                    <div id="{keyword}" class="tab-content {active_class}">
                        <div class="iframe-container">
                            <iframe src="../figures/html/{safe_filename}_vs_price_interactive.html" frameborder="0"></iframe>
                        </div>
                    </div>
            '''
        
        # Add JavaScript for tab functionality
        dashboard_html += '''
                </div>
                
                <div class="footer">
                    <p>Dashboard generated on ''' + time.strftime("%Y-%m-%d %H:%M:%S") + '''</p>
                </div>
            </div>
            
            <script>
                function openTab(evt, keywordName) {
                    // Hide all tab content
                    var tabcontent = document.getElementsByClassName("tab-content");
                    for (var i = 0; i < tabcontent.length; i++) {
                        tabcontent[i].className = tabcontent[i].className.replace(" active", "");
                    }
                    
                    // Remove active class from all tabs
                    var tabs = document.getElementsByClassName("keyword-tab");
                    for (var i = 0; i < tabs.length; i++) {
                        tabs[i].className = tabs[i].className.replace(" active", "");
                    }
                    
                    // Show the specific tab content
                    document.getElementById(keywordName).className += " active";
                    
                    // Add active class to the button that opened the tab
                    evt.currentTarget.className += " active";
                }
            </script>
        </body>
        </html>
        '''
        
        # Create directory if needed
        os.makedirs('dashboard', exist_ok=True)
        
        # Write dashboard file
        dashboard_path = 'dashboard/keyword_trends.html'
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(dashboard_html)
            
        print(f"✅ Successfully generated dashboard at {dashboard_path}")
        
        return dashboard_path
        
    except Exception as e:
        print(f"❌ Error generating dashboard: {str(e)}")
        return None

def fix_dashboard_paths(dashboard_path):
    """Fix relative paths in dashboard for Docker compatibility"""
    try:
        # Read the dashboard HTML
        with open(dashboard_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Fix the paths - replace all references to ../figures/
        fixed_content = content.replace('../figures/', './figures/')
        
        # Write the fixed content back
        with open(dashboard_path, 'w', encoding='utf-8') as file:
            file.write(fixed_content)
            
        print("✅ Fixed paths in dashboard for Docker compatibility")
        
        # Also copy figures to dashboard directory for direct access
        import shutil, os
        if os.path.exists('figures'):
            # Copy HTML directory
            if os.path.exists('figures/html'):
                os.makedirs('dashboard/figures/html', exist_ok=True)
                for file in os.listdir('figures/html'):
                    shutil.copy2(f'figures/html/{file}', f'dashboard/figures/html/{file}')
            
            # Copy PNG files
            for file in os.listdir('figures'):
                if file.endswith('.png'):
                    shutil.copy2(f'figures/{file}', f'dashboard/{file}')
        
        return True
    except Exception as e:
        print(f"⚠️ Error fixing dashboard paths: {str(e)}")
        return False

def main():
    """Run the main analysis pipeline."""
    try:
        print("\n================================================================================")
        print("🔎 BITCOIN NEWS KEYWORD TREND ANALYSIS 🔎")
        print("================================================================================")
        print("Analyzing Bitcoin-related news to identify trending keywords")
        print("and correlate their frequency with Bitcoin price movements.")
        print("================================================================================\n\n")
        
        # Ensure necessary directories exist
        ensure_directories()
        
        # Check if running in Docker
        running_in_docker = utils.is_docker()
        if running_in_docker:
            print("🐳 Running inside Docker container")
        
        # Fetch current Bitcoin price first (for dashboard)
        print("\n💰 Fetching current Bitcoin price...")
        current_price = utils.fetch_current_bitcoin_price()
        if current_price:
            print(f"✅ Current Bitcoin price: ${current_price['price']:,.2f}")
        else:
            print("⚠️ Could not get current Bitcoin price. Dashboard will use historical or sample data.")
        
        # Step 1: Fetch news data - use 30 days to stay within free API limits
        print("\n📰 Fetching Bitcoin news articles...")
        news_data = utils.fetch_bitcoin_news(days=30, query='bitcoin OR cryptocurrency', language='en')
        
        # If news data could not be fetched, use sample data
        if news_data is None:
            print("⚠️ No news data retrieved. Using sample data for demonstration...")
            # Create sample data for demonstration
            dates = pd.date_range(start='2023-05-01', periods=5)
            sample_articles = []
            
            for i, date in enumerate(dates):
                sample_articles.append({
                    'title': f"Sample Bitcoin Article {i+1}",
                    'description': f"This is a sample article about Bitcoin and cryptocurrency for demonstration purposes.",
                    'publishedAt': date,
                    'source': {'name': 'Sample News'},
                    'url': 'https://example.com',
                    'urlToImage': '',
                    'fetched_date': date.strftime('%Y-%m-%d')
                })
            
            news_data = pd.DataFrame(sample_articles)
            news_data['publishedAt'] = pd.to_datetime(news_data['publishedAt'])
            news_data['date'] = news_data['publishedAt'].dt.date
            news_data['hour'] = news_data['publishedAt'].dt.hour
            
            # Save the sample data
            news_data.to_csv('data/bitcoin_news.csv', index=False)
            print("✅ Sample news data created")
        else:
            print(f"✅ Successfully fetched {len(news_data)} news articles")
        
        # Step 2: Fetch price data - use daily data since we don't have enough hourly data points
        print("\n💰 Fetching Bitcoin price data...")
        price_df = utils.fetch_bitcoin_prices(days=30, interval='daily')
        
        if price_df is None:
            print("⚠️ No price data retrieved. Using sample data for demonstration...")
            # Create sample price data that mirrors actual Bitcoin behavior
            dates = pd.date_range(start='2023-05-01', periods=5)
            sample_prices = {
                'timestamp': dates,
                'price': [50000, 51200, 49800, 52300, 53100], 
                'date': [d.date() for d in dates],
                'hour': [0, 0, 0, 0, 0]
            }
            price_df = pd.DataFrame(sample_prices)
            
            # Save the sample data
            price_df.to_csv('data/bitcoin_prices.csv', index=False)
            print("✅ Sample price data created")
        else:
            print(f"✅ Successfully fetched {len(price_df)} price data points")
    
        # Step 3: Process data - extract keywords
        print("\n🔑 Extracting keywords from news articles...")
        news_with_keywords = utils.extract_keywords(min_frequency=1, include_titles=True)
        
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
        trend_data = utils.analyze_trends(
            time_window='daily', 
            min_freq=5,      # Minimum keyword frequency for reliable correlation
            min_days=5,      # Require keywords to appear on multiple days for better statistics
            verbose=False    # Suppress detailed correlation warnings
        )
        
        if trend_data is None or trend_data.empty:
            print("❌ Trend analysis failed. Cannot proceed with visualization.")
            return
        
        # Small delay to make sure files are written
        time.sleep(1)
        
        # Step 5: Run Granger causality tests with appropriate parameters for limited data
        print("\n🧪 Running Granger causality tests...")
        
        # Check if we have enough data for meaningful Granger tests
        keyword_counts = trend_data.groupby('keyword').size()
        print(f"📊 Found {len(keyword_counts)} unique keywords for causality testing")
        
        # For daily data, we need at least 20 data points for reliable causality testing
        # But use what we have with appropriate limitations
        if len(price_df) >= 25:
            print("📊 Sufficient data available for basic causality tests")
            causality_results = utils.run_granger_tests(top_n=10, max_lag=3, min_data_points=15)
        elif len(price_df) >= 15:
            print("📊 Limited data available - using reduced test parameters")
            causality_results = utils.run_granger_tests(top_n=8, max_lag=2, min_data_points=10)
        else:
            print("⚠️ Very limited data for causality testing. Using minimal parameters.")
            print("⚠️ Results should be considered preliminary and may not be statistically reliable.")
            causality_results = utils.run_granger_tests(top_n=5, max_lag=1, min_data_points=5)
        
        # Step 6: Generate visualizations
        print("\n📊 Generating visualizations...")
        
        # Get top keywords - handle edge cases
        if 'keyword' in trend_data.columns:
            # Prioritize significant keywords from Granger tests if available
            significant_keywords = []
            if causality_results is not None and 'k2p_significant' in causality_results.columns:
                significant_keywords = causality_results[causality_results['k2p_significant']]['keyword'].tolist()
                if significant_keywords:
                    print(f"📊 Found {len(significant_keywords)} statistically significant keywords: {', '.join(significant_keywords)}")
            
            # Use top frequent keywords for visualization but prefer crypto-related keywords
            crypto_related = ['bitcoin', 'btc', 'crypto', 'cryptocurrency', 'blockchain', 
                             'ethereum', 'eth', 'defi', 'nft', 'mining', 'halving']
            
            # Get crypto-related keywords from the top
            trend_data_sorted = trend_data.sort_values('frequency', ascending=False)
            crypto_keywords = [k for k in trend_data_sorted['keyword'].tolist() 
                              if any(term in k.lower() for term in crypto_related)][:5]
            
            # Get top correlation keywords (both positive and negative)
            # Filter out keywords with too few data points for reliability
            reliable_trends = trend_data[trend_data['days'] >= 7]
            if len(reliable_trends) >= 10:
                correlation_keywords = (
                    reliable_trends.nlargest(5, 'correlation')['keyword'].tolist() + 
                    reliable_trends.nsmallest(5, 'correlation')['keyword'].tolist()
                )
            else:
                correlation_keywords = (
                    trend_data.nlargest(5, 'correlation')['keyword'].tolist() + 
                    trend_data.nsmallest(5, 'correlation')['keyword'].tolist()
                )
            
            # Combine all keyword sources with priorities
            all_keywords = significant_keywords + crypto_keywords + correlation_keywords
            
            # Remove duplicates while preserving order
            top_keywords = []
            for k in all_keywords:
                if k not in top_keywords:
                    top_keywords.append(k)
            
            # Truncate to 10 keywords
            top_keywords = top_keywords[:10]
            
            print(f"📊 Selected keywords for visualization: {', '.join(top_keywords)}")
        else:
            print("⚠️ Missing keyword column in trend data. Using default keywords.")
            top_keywords = ['bitcoin', 'price', 'market']
        
        # Display correlation heatmap with top keywords - use more selective filtering
        print("\n📊 Creating correlation heatmap...")
        utils.plot_keyword_price_heatmap(
            top_n=15,  # Reduced to avoid scroll bar
            save_fig=True,
            display_fig=False
        )
        
        # Allow time between visualizations
        time.sleep(1)
        
        # Create individual keyword charts
        for keyword in top_keywords:
            print(f"\n📈 Creating visualization for keyword '{keyword}'...")
            utils.plot_keyword_vs_price(
                keyword,
                save_fig=True,
                display_fig=False
            )
            # Allow time between visualizations
            time.sleep(1)
        
        # Step 7: Generate dashboard
        print("\n📊 Generating interactive dashboard...")
        dashboard_path = generate_dashboard(top_keywords, trend_data, causality_results, current_price)
        
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
        print(f"📰 Analyzed {len(news_data)} news articles over 30 days")
        print(f"💰 Used daily price data for time series analysis")
        print(f"🔑 Extracted {len(trend_data)} unique keywords")
        print(f"📈 Top keywords: {', '.join(top_keywords[:5])}")
        
        # Show where to find results
        print("\n📁 OUTPUT FILES 📁")
        print("=" * 40)
        print("📊 Data files saved in: ./data/")
        print("📈 Visualizations saved in: ./figures/")
        
        if dashboard_path:
            print(f"🌐 Interactive dashboard: {dashboard_path}")
            
            if running_in_docker:
                fix_dashboard_paths(dashboard_path)
                print("\n📊 Visualizations have been fixed for Docker compatibility.")
            else:
                print("📊 Dashboard has been opened in your browser.")

    except Exception as e:
        print("\n❌ Error during analysis:")
        print(str(e))
        if "-v" in sys.argv or "--verbose" in sys.argv:
            traceback.print_exc()

def open_dashboard(dashboard_path):
    """Open the dashboard in a browser, works on all platforms."""
    import os
    import webbrowser
    import time
    import platform
    import subprocess

    # Wait for the file to be fully written
    time.sleep(2)
    
    if not os.path.exists(dashboard_path):
        print(f"⚠️ Dashboard file not found at {dashboard_path}")
        return False

    # Get absolute path
    abs_path = os.path.abspath(dashboard_path)
    file_uri = 'file:///' + abs_path.replace('\\', '/').replace(' ', '%20')
    
    print(f"🌐 Opening dashboard at: {file_uri}")
    
    # Method 1: Use webbrowser module (most universal)
    try:
        webbrowser.open(file_uri, new=2)  # new=2 means open in new tab
        return True
    except Exception as e:
        print(f"Method 1 failed: {str(e)}")
    
    # Method 2: Use platform-specific commands
    try:
        system = platform.system().lower()
        if system == 'windows':
            os.startfile(abs_path)
        elif system == 'darwin':  # macOS
            subprocess.Popen(['open', abs_path])
        elif system == 'linux':
            subprocess.Popen(['xdg-open', abs_path])
        return True
    except Exception as e:
        print(f"Method 2 failed: {str(e)}")
    
    print("⚠️ Could not open dashboard automatically. Please open it manually.")
    return False

def check_environment():
    """Check if the environment has the necessary components."""
    try:
        import pandas as pd
        import numpy as np
        import requests
        import matplotlib.pyplot as plt
        import seaborn as sns
        import plotly.express as px
        from textblob import TextBlob
        from statsmodels.tsa.stattools import grangercausalitytests
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {str(e)}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    

if __name__ == "__main__":
    if check_environment():
        main() 