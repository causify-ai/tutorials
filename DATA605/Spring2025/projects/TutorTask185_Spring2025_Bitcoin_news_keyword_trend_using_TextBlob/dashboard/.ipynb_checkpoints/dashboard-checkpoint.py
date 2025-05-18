import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import sys
import json
from datetime import datetime

# Add root directory to path
sys.path.append('..')

def load_data():
    """Load the necessary data files for the dashboard."""
    data_files = {
        'news': 'data/bitcoin_news_with_keywords.csv',
        'prices': 'data/bitcoin_prices.csv',
        'merged': 'data/merged_keyword_price.csv',
        'trends': 'data/keyword_trends.csv',
        'granger': 'data/granger_causality_results.csv'
    }
    
    data = {}
    for key, filepath in data_files.items():
        full_path = os.path.join('..', filepath)
        if os.path.exists(full_path):
            data[key] = pd.read_csv(full_path)
            if key in ['news', 'prices', 'merged']:
                # Convert date columns
                date_cols = [col for col in data[key].columns if 'date' in col.lower() or 'time' in col.lower()]
                for col in date_cols:
                    try:
                        data[key][col] = pd.to_datetime(data[key][col])
                    except:
                        pass
        else:
            print(f"Warning: {filepath} not found")
    
    return data

def create_keyword_trend_chart(data, top_n=5):
    """Create a chart showing trending keywords over time."""
    if 'merged' not in data or data['merged'].empty:
        return None
        
    df = data['merged'].copy()
    
    # Get top keywords by frequency
    top_keywords = df['keyword'].value_counts().nlargest(top_n).index.tolist()
    
    # Filter for top keywords
    df = df[df['keyword'].isin(top_keywords)]
    
    # Create figure
    fig = px.line(df, x='time_window', y='count', color='keyword',
                 title=f'Top {top_n} Keyword Trends Over Time',
                 labels={'time_window': 'Date', 'count': 'Frequency', 'keyword': 'Keyword'})
                 
    fig.update_layout(
        template='plotly_white',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=40, r=40, t=40, b=40)
    )
    
    return fig

def create_price_correlation_chart(data):
    """Create a chart showing keyword correlations with Bitcoin price."""
    if 'trends' not in data or data['trends'].empty:
        return None
        
    df = data['trends'].copy()
    
    # Sort by absolute correlation
    df['abs_corr'] = df['correlation'].abs()
    df = df.sort_values('abs_corr', ascending=False).head(10)
    
    # Create figure
    fig = px.bar(df, y='keyword', x='correlation', color='correlation',
                color_continuous_scale=px.colors.diverging.RdBu_r,
                title='Keyword Correlation with Bitcoin Price',
                labels={'correlation': 'Correlation Coefficient', 'keyword': 'Keyword'})
                
    fig.update_layout(
        template='plotly_white',
        margin=dict(l=40, r=40, t=40, b=40),
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig

def create_granger_causality_chart(data):
    """Create a chart showing Granger causality test results."""
    if 'granger' not in data or data['granger'].empty:
        return None
        
    df = data['granger'].copy()
    
    # Create figure
    fig = make_subplots(rows=1, cols=2, 
                       subplot_titles=('Keywords → Price', 'Price → Keywords'),
                       shared_yaxes=True)
                       
    # Keywords to price
    df_sorted = df.sort_values('k2p_pvalue')
    fig.add_trace(
        go.Bar(
            y=df_sorted['keyword'],
            x=df_sorted['k2p_pvalue'],
            orientation='h',
            marker_color=['rgba(0, 128, 0, 0.7)' if x else 'rgba(128, 128, 128, 0.7)' for x in df_sorted['k2p_significant']],
            name='Keywords → Price',
            hovertemplate='p-value: %{x:.4f}<br>Significant: %{text}',
            text=df_sorted['k2p_significant']
        ),
        row=1, col=1
    )
    
    # Price to keywords
    df_sorted = df.sort_values('p2k_pvalue')
    fig.add_trace(
        go.Bar(
            y=df_sorted['keyword'],
            x=df_sorted['p2k_pvalue'],
            orientation='h',
            marker_color=['rgba(0, 128, 0, 0.7)' if x else 'rgba(128, 128, 128, 0.7)' for x in df_sorted['p2k_significant']],
            name='Price → Keywords',
            hovertemplate='p-value: %{x:.4f}<br>Significant: %{text}',
            text=df_sorted['p2k_significant']
        ),
        row=1, col=2
    )
    
    # Add significance line
    fig.add_vline(x=0.05, line_dash='dash', line_color='red', row=1, col=1)
    fig.add_vline(x=0.05, line_dash='dash', line_color='red', row=1, col=2)
    
    fig.update_layout(
        title_text='Granger Causality Test Results (p < 0.05 is significant)',
        template='plotly_white',
        height=400 + len(df) * 20,
        margin=dict(l=40, r=40, t=60, b=40),
        showlegend=False
    )
    
    return fig

def create_keyword_price_overlay(data, keyword):
    """Create a chart overlaying a specific keyword frequency with Bitcoin price."""
    if 'merged' not in data or data['merged'].empty:
        return None
        
    df = data['merged'].copy()
    keyword_data = df[df['keyword'] == keyword]
    
    if keyword_data.empty:
        return None
        
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add keyword frequency trace
    fig.add_trace(
        go.Scatter(
            x=keyword_data['time_window'],
            y=keyword_data['count'],
            name=f'"{keyword}" mentions',
            line=dict(color='blue')
        ),
        secondary_y=False
    )
    
    # Add price trace
    fig.add_trace(
        go.Scatter(
            x=keyword_data['time_window'],
            y=keyword_data['price'],
            name='Bitcoin Price (USD)',
            line=dict(color='orange')
        ),
        secondary_y=True
    )
    
    # Update layout
    fig.update_layout(
        title_text=f'"{keyword}" Mentions vs. Bitcoin Price',
        template='plotly_white',
        margin=dict(l=40, r=40, t=40, b=40),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='x unified'
    )
    
    # Set y-axes titles
    fig.update_yaxes(title_text=f'"{keyword}" Frequency', secondary_y=False, color='blue')
    fig.update_yaxes(title_text="Bitcoin Price (USD)", secondary_y=True, color='orange')
    
    return fig

def generate_dashboard():
    """Generate a comprehensive dashboard for Bitcoin news keyword analysis."""
    
    # Create necessary directories
    os.makedirs('dashboard/assets', exist_ok=True)
    
    # Get Bitcoin price data - first check for real-time data
    current_price_data = None
    using_real_time_data = False
    try:
        if os.path.exists('data/current_price.json'):
            with open('data/current_price.json', 'r') as f:
                current_price_data = json.load(f)
                
            # Check if the data is recent (less than 1 hour old)
            if 'timestamp' in current_price_data:
                timestamp = datetime.fromisoformat(current_price_data['timestamp'])
                if (datetime.now() - timestamp).total_seconds() < 3600:  # 1 hour
                    using_real_time_data = True
                    print("[SUCCESS] Using real-time Bitcoin price data")
    except Exception as e:
        print(f"[WARNING] Error loading current price data: {str(e)}")
    
    # If no real-time data, try to use historical data
    historical_price_data = None
    if not using_real_time_data and os.path.exists('data/bitcoin_prices.csv'):
        try:
            price_df = pd.read_csv('data/bitcoin_prices.csv')
            if 'price' in price_df.columns and not price_df.empty:
                historical_price_data = {
                    'price': price_df['price'].iloc[-1],
                    'min': price_df['price'].min(),
                    'max': price_df['price'].max(),
                    'change': ((price_df['price'].iloc[-1] / price_df['price'].iloc[0]) - 1) * 100
                }
                print("[SUCCESS] Using historical Bitcoin price data")
        except Exception as e:
            print(f"[WARNING] Error loading historical price data: {str(e)}")
    
    # Generate the HTML dashboard
    html = generate_html_dashboard(current_price_data, historical_price_data, using_real_time_data)
    
    # Save the dashboard
    with open('dashboard/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"[SUCCESS] Dashboard generated at {os.path.abspath('dashboard/index.html')}")
    return os.path.abspath('dashboard/index.html')

def generate_html_dashboard(current_price_data, historical_price_data, using_real_time_data):
    """Generate the HTML for the dashboard."""
    
    # Start HTML
    html = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bitcoin News Keyword Analysis</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary-color: #f2a900;
                --secondary-color: #4d4d4d;
                --background-color: #f9f9f9;
                --card-bg: #ffffff;
                --text-color: #333333;
                --border-color: #e0e0e0;
                --positive: #28a745;
                --negative: #dc3545;
                --header-bg-start: #2c2c2c;
                --header-bg-end: #434343;
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Roboto', sans-serif;
                line-height: 1.6;
                color: var(--text-color);
                background-color: var(--background-color);
                padding: 0;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            
            header {
                background: linear-gradient(135deg, var(--header-bg-start), var(--header-bg-end));
                color: white;
                padding: 2rem;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            
            h1 {
                font-size: 2.5rem;
                margin-bottom: 0.5rem;
            }
            
            h2 {
                color: var(--primary-color);
                margin: 1.5rem 0 1rem;
                border-bottom: 2px solid var(--primary-color);
                padding-bottom: 0.5rem;
            }
            
            h3 {
                color: var(--secondary-color);
                margin: 1rem 0;
            }
            
            .subtitle {
                font-weight: 300;
                color: rgba(255,255,255,0.9);
            }
            
            .timestamp {
                background-color: rgba(0,0,0,0.1);
                padding: 0.5rem 1rem;
                border-radius: 20px;
                display: inline-block;
                margin-top: 1rem;
                font-size: 0.9rem;
            }
            
            .current-price {
                font-size: 2.5rem;
                font-weight: 700;
                color: white;
                margin-top: 1rem;
                text-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }
            
            .price-change {
                font-size: 1.2rem;
                font-weight: 500;
                padding: 0.25rem 0.75rem;
                border-radius: 20px;
                display: inline-block;
                margin-left: 0.5rem;
            }
            
            .positive-change {
                background-color: rgba(40, 167, 69, 0.3);
                color: white;
            }
            
            .negative-change {
                background-color: rgba(220, 53, 69, 0.3);
                color: white;
            }
            
            .card {
                background-color: var(--card-bg);
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                padding: 1.5rem;
                margin-bottom: 2rem;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }
            
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 6px 12px rgba(0,0,0,0.15);
            }
            
            .stats-row {
                display: flex;
                flex-wrap: wrap;
                gap: 15px;
                margin-bottom: 1.5rem;
            }
            
            .stat-card {
                flex: 1;
                min-width: 150px;
                background-color: var(--card-bg);
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                padding: 1rem;
                text-align: center;
                border-left: 4px solid var(--primary-color);
            }
            
            .stat-title {
                font-size: 0.9rem;
                color: var(--secondary-color);
                margin-bottom: 0.5rem;
            }
            
            .stat-value {
                font-size: 1.4rem;
                font-weight: 700;
                color: var(--primary-color);
            }
            
            .flex-container {
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
            }
            
            .correlation-card {
                flex: 1 1 100%;
            }
            
            .keyword-card {
                flex: 1 1 calc(50% - 20px);
                min-width: 300px;
            }
            
            img {
                max-width: 100%;
                height: auto;
                border-radius: 4px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin: 0.5rem 0;
            }
            
            .footer {
                text-align: center;
                padding: 2rem;
                color: var(--secondary-color);
                font-size: 0.9rem;
                border-top: 1px solid var(--border-color);
                margin-top: 2rem;
            }
            
            .bitcoin-logo {
                display: inline-block;
                width: 46px;
                height: 46px;
                background-color: var(--primary-color);
                color: white;
                font-weight: bold;
                font-style: italic;
                font-size: 26px;
                border-radius: 50%;
                line-height: 46px;
                text-align: center;
                margin-right: 10px;
                vertical-align: middle;
                transform: rotate(0deg);
                padding-left: 3px;
                font-family: Arial, sans-serif;
                position: relative;
                box-shadow: 0 2px 5px rgba(0,0,0,0.3);
            }
            
            .data-badge {
                font-size: 0.8rem;
                color: #856404;
                background-color: #fff3cd;
                padding: 3px 8px;
                border-radius: 12px;
                margin-left: 10px;
                vertical-align: middle;
            }
            
            .real-time-badge {
                font-size: 0.8rem;
                color: #155724;
                background-color: #d4edda;
                padding: 3px 8px;
                border-radius: 12px;
                margin-left: 10px;
                vertical-align: middle;
            }
            
            .disclaimer {
                background-color: rgba(255, 248, 225, 0.9);
                border-left: 4px solid #ffc107;
                padding: 10px 15px;
                margin: 15px 0;
                border-radius: 4px;
                font-size: 0.9rem;
                color: #856404;
            }
            
            .chart-note {
                font-size: 0.9rem;
                color: #666;
                font-style: italic;
                margin-top: 10px;
                text-align: center;
            }
            
            @media (max-width: 768px) {
                .keyword-card {
                    flex: 1 1 100%;
                }
                h1 {
                    font-size: 2rem;
                }
            }
        </style>
    </head>
    <body>
        <header>
            <div class="container">
                <h1><span class="bitcoin-logo">&#8383;</span> Bitcoin News Keyword Analysis</h1>
                <p class="subtitle">Analyzing Cryptocurrency News Keywords and Price Correlations</p>
    """
    
    # Add current price to header if available
    if using_real_time_data and current_price_data:
        change_24h = current_price_data.get('change_24h', 0)
        change_class = "positive-change" if change_24h >= 0 else "negative-change"
        change_sign = "+" if change_24h >= 0 else ""
        
        html += f"""
                <div class="current-price">
                    ${current_price_data['price']:,.2f}
                    <span class="price-change {change_class}">{change_sign}{change_24h:.2f}%</span>
                </div>
        """
    
    html += f"""
                <div class="timestamp">Generated on {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</div>
            </div>
        </header>
        
        <div class="container">
    """
    
    # Add disclaimer based on data source
    if not using_real_time_data:
        html += """
            <div class="disclaimer">
                <strong>Note:</strong> This dashboard is using historical or sample data for Bitcoin prices. 
                The price information shown is not real-time market data.
            </div>
        """
    
    # Price overview section
    html += f"""
            <div class="card">
                <h2>Bitcoin Price Overview 
                    <span class="{'real-time-badge' if using_real_time_data else 'data-badge'}">
                        {('Real-time Data' if using_real_time_data else 'Sample Data')}
                    </span>
                </h2>
                <div class="stats-row">
    """
    
    # Add stats based on the available data
    if using_real_time_data and current_price_data:
        html += f"""
                    <div class="stat-card">
                        <div class="stat-title">Current Price</div>
                        <div class="stat-value">${current_price_data['price']:,.2f}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-title">24h Change</div>
                        <div class="stat-value" style="color: {'var(--positive)' if current_price_data['change_24h'] >= 0 else 'var(--negative)'}">
                            {'+' if current_price_data['change_24h'] >= 0 else ''}{current_price_data['change_24h']:.2f}%
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-title">Market Cap</div>
                        <div class="stat-value">${current_price_data['market_cap'] / 1_000_000_000:.2f}B</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-title">24h Volume</div>
                        <div class="stat-value">${current_price_data['vol_24h'] / 1_000_000_000:.2f}B</div>
                    </div>
        """
    elif historical_price_data:
        html += f"""
                    <div class="stat-card">
                        <div class="stat-title">Current Price</div>
                        <div class="stat-value">${historical_price_data['price']:,.2f}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-title">Price Change</div>
                        <div class="stat-value" style="color: {'var(--positive)' if historical_price_data['change'] >= 0 else 'var(--negative)'}">
                            {'+' if historical_price_data['change'] >= 0 else ''}{historical_price_data['change']:.2f}%
                        </div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-title">Period Low</div>
                        <div class="stat-value">${historical_price_data['min']:,.2f}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-title">Period High</div>
                        <div class="stat-value">${historical_price_data['max']:,.2f}</div>
                    </div>
        """
    else:
        # Fallback to sample data if no real data is available
        html += """
                    <div class="stat-card">
                        <div class="stat-title">Current Price</div>
                        <div class="stat-value">$50,000.00</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-title">Price Change</div>
                        <div class="stat-value" style="color: var(--positive)">+2.5%</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-title">Period Low</div>
                        <div class="stat-value">$48,500.00</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-title">Period High</div>
                        <div class="stat-value">$51,200.00</div>
                    </div>
        """
        
    html += """
                </div>
            </div>
    """
    
    # Add keyword-price correlation section
    if os.path.exists('figures/keyword_price_correlation.png'):
        html += """
            <div class="card correlation-card">
                <h2>Keyword-Price Correlations</h2>
                <p>This heatmap shows how different keywords in news correlate with Bitcoin price movements.</p>
                <img src="assets/keyword_price_correlation.png" alt="Keyword Correlations">
            </div>
            
            <h2>Keyword Trend Analysis</h2>
        """
        
        html += """
            <div class="flex-container">
        """
    
    # Add individual keyword visualizations
    if os.path.exists('data/keyword_trends.csv'):
        try:
            trends_df = pd.read_csv('data/keyword_trends.csv')
            top_keywords = trends_df.nlargest(5, 'frequency')['keyword'].tolist()
            
            for keyword in top_keywords:
                # Sanitize the keyword for filename
                import re
                safe_name = re.sub(r'[<>:"\\|?*]', '_', keyword).strip('. ').replace(' ', '_')
                
                if os.path.exists(f'figures/{safe_name}_vs_price.png'):
                    html += f"""
                        <div class="card keyword-card">
                            <h3>'{keyword}' Trend Analysis</h3>
                            <img src="assets/{safe_name}_vs_price.png" alt="{keyword} vs Price">
                        </div>
                    """
                    
                    # Copy the image to assets
                    try:
                        import shutil
                        shutil.copy(f'figures/{safe_name}_vs_price.png', 'dashboard/assets/')
                    except Exception as e:
                        print(f"[WARNING] Could not copy image for {keyword}: {str(e)}")
        except Exception as e:
            print(f"[WARNING] Error processing keyword trends: {str(e)}")
    
    # Close the flex container
    html += """
            </div>
    """
    
    # Add Granger causality results if available
    if os.path.exists('figures/granger_causality_tests.png'):
        html += """
            <div class="card">
                <h2>Granger Causality Test Results</h2>
                <p>Granger causality tests determine if one time series can predict another.</p>
                <img src="assets/granger_causality_tests.png" alt="Granger Causality Tests">
            </div>
        """
        
        # Copy the image to assets
        try:
            import shutil
            shutil.copy('figures/granger_causality_tests.png', 'dashboard/assets/')
        except Exception as e:
            print(f"[WARNING] Could not copy Granger causality image: {str(e)}")
    
    # Add footer and close HTML
    html += """
            <div class="footer">
                <p>Created with TextBlob, Matplotlib, and Python | Bitcoin News Keyword Analysis | Data Analysis Project</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

if __name__ == "__main__":
    generate_dashboard() 