# visualize.py
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np
import warnings
import sys
import re
import webbrowser
from tempfile import NamedTemporaryFile
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import subprocess
import shutil
import json
import time

# Suppress specific warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Check if running in Docker
def is_docker():
    """Check if running inside a Docker container"""
    path = '/proc/self/cgroup'
    return os.path.exists('/.dockerenv') or os.path.isfile(path) and any('docker' in line for line in open(path))

# Default display behavior based on environment
DEFAULT_DISPLAY = not is_docker()

def sanitize_filename(filename):
    """
    Sanitize a string to make it safe for use as a filename.
    Removes or replaces characters that are problematic in filenames.
    """
    # Replace angle brackets, quotes, and other problematic characters
    sanitized = re.sub(r'[<>:"\\|?*]', '_', filename)
    # Remove any leading/trailing spaces and periods
    sanitized = sanitized.strip('. ')
    # Replace multiple underscores with a single one
    sanitized = re.sub(r'_+', '_', sanitized)
    # Ensure the filename is not empty
    if not sanitized:
        sanitized = "unnamed"
    return sanitized

def plot_keyword_vs_price(keyword, save_fig=True, display_fig=False):
    """Create a visualization comparing keyword frequency with Bitcoin price."""
    try:
        if not os.path.exists('data/merged_keyword_price.csv'):
            print("❌ No merged data found. Please run analyze_trends() first.")
            return None
        df = pd.read_csv('data/merged_keyword_price.csv')
        keyword_data = df[df['keyword'] == keyword]
        if keyword_data.empty:
            print(f"❌ No data found for keyword '{keyword}'")
            return None
            
        # Convert date column
        keyword_data['time_window'] = pd.to_datetime(keyword_data['time_window'])
            
        # Calculate correlation
        correlation = keyword_data['count'].corr(keyword_data['price'])
        corr_color = 'green' if correlation > 0 else 'red'
        
        # Create enhanced figure with matplotlib
        plt.figure(figsize=(10, 6))
        ax1 = plt.gca()
        ax2 = ax1.twinx()
        
        # Plot keyword frequency with enhanced styling
        keyword_line = ax1.plot(keyword_data['time_window'], keyword_data['count'], color='#1f77b4', marker='o', markersize=6, 
                   linewidth=2, label='Keyword Frequency', zorder=2)
        ax1.set_xlabel('Date', fontsize=11, fontweight='bold')
        ax1.set_ylabel(f"'{keyword}' Frequency", color='#1f77b4', fontsize=11, fontweight='bold')
        ax1.tick_params(axis='y', labelcolor='#1f77b4', labelsize=9)
        ax1.grid(axis='y', alpha=0.3)
        
        # Add padding to y-axis to prevent overlap
        y_min, y_max = ax1.get_ylim()
        padding = (y_max - y_min) * 0.1
        ax1.set_ylim(y_min, y_max + padding)
        
        # Fill area under keyword frequency curve
        ax1.fill_between(keyword_data['time_window'], 0, keyword_data['count'], color='#1f77b4', alpha=0.2)
        
        # Plot Bitcoin price with enhanced styling
        price_line = ax2.plot(keyword_data['time_window'], keyword_data['price'], color='#ff7f0e', marker='s', markersize=6,
                   linewidth=2, label='Bitcoin Price', zorder=1)
        ax2.set_ylabel('Bitcoin Price (USD)', color='#ff7f0e', fontsize=11, fontweight='bold')
        ax2.tick_params(axis='y', labelcolor='#ff7f0e', labelsize=9)
        
        # Set price labels with $ formatting
        ax2.yaxis.set_major_formatter('${x:,.0f}')
        
        # Format x-axis dates better
        import matplotlib.dates as mdates
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d %H:%M'))
        
        # Title with better positioning
        plt.title(f"'{keyword}' Frequency vs Bitcoin Price\nCorrelation: {correlation:.3f}", 
                 fontsize=14, fontweight='bold', color='black', pad=10)
        
        # Highlight correlation value
        corr_text = ax1.text(0.02, 0.95, f"Correlation: {correlation:.3f}", transform=ax1.transAxes,
                fontsize=10, fontweight='bold', color=corr_color,
                bbox=dict(facecolor='white', alpha=0.8, edgecolor=corr_color, boxstyle='round,pad=0.3'))
        
        # Add legend with better positioning
        lines = keyword_line + price_line
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper right', fontsize=9, framealpha=0.9)
        
        # Add date grid lines
        ax1.grid(axis='x', alpha=0.3)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')
        plt.subplots_adjust(bottom=0.20)  # Add more space at the bottom for rotated labels
        
        if save_fig:
            os.makedirs('figures', exist_ok=True)
            safe_filename = sanitize_filename(keyword)
            plt.savefig(f'figures/{safe_filename}_vs_price.png', dpi=300, bbox_inches='tight')
            print(f"✅ Saved visualization to figures/{safe_filename}_vs_price.png")
        
        if display_fig:
            plt.show()
        else:
            plt.close()
            
        # Create an enhanced Plotly version for more interactive visualization
        try:
            # Create a more appealing color scheme
            bitcoin_color = '#f2a900'  # Bitcoin gold
            keyword_color = '#0052cc'  # Strong blue
            
            # Create figure with custom layout
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Add keyword frequency trace
            fig.add_trace(
                go.Scatter(
                    x=keyword_data['time_window'], 
                    y=keyword_data['count'],
                    name=f"{keyword} mentions",
                    mode="lines+markers",
                    line=dict(width=2, color=keyword_color),
                    marker=dict(size=7, color=keyword_color),
                    hovertemplate='Date: %{x}<br>Mentions: %{y}<extra></extra>',
                    fill='tozeroy',
                    fillcolor=f'rgba(0, 82, 204, 0.1)'
                ),
                secondary_y=False,
            )
            
            # Add Bitcoin price trace
            fig.add_trace(
                go.Scatter(
                    x=keyword_data['time_window'], 
                    y=keyword_data['price'],
                    name="Bitcoin Price (USD)",
                    mode="lines+markers",
                    line=dict(width=2, color=bitcoin_color),
                    marker=dict(size=7, color=bitcoin_color),
                    hovertemplate='Date: %{x}<br>Price: $%{y:,.2f}<extra></extra>'
                ),
                secondary_y=True,
            )
            
            # Add annotation for correlation
            corr_color = 'green' if correlation > 0 else 'red'
            
            fig.add_annotation(
                x=0.01,
                y=0.98,
                xref="paper",
                yref="paper",
                text=f"Correlation: {correlation:.3f}",
                showarrow=False,
                font=dict(
                    size=12,
                    color=corr_color
                ),
                align="left",
                bgcolor="rgba(255, 255, 255, 0.8)",
                bordercolor=corr_color,
                borderwidth=2,
                borderpad=4,
                opacity=0.8
            )
            
            # Update layout for better appearance
            fig.update_layout(
                title={
                    'text': f"'{keyword}' Frequency vs Bitcoin Price",
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': dict(size=24, color="#333333")
                },
                hovermode="x unified",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="center",
                    x=0.5
                ),
                plot_bgcolor='rgba(250,250,250,0.9)',
                paper_bgcolor='rgba(250,250,250,0.9)',
                height=700
            )
            
            # Update axes with improved date formatting
            fig.update_xaxes(
                title_text="Date",
                title_font=dict(size=14),
                gridcolor='rgba(211,211,211,0.3)',
                showline=True,
                linewidth=1,
                linecolor='rgba(211,211,211,0.8)',
                tickangle=45,
                tickformat="%b %d %H:%M"  # Format as "Jan 01 12:00"
            )
            
            fig.update_yaxes(
                title_text=f"{keyword} Frequency",
                title_font=dict(size=14, color=keyword_color),
                tickfont=dict(color=keyword_color),
                gridcolor='rgba(211,211,211,0.3)',
                showline=True,
                linewidth=1,
                linecolor=keyword_color,
                secondary_y=False
            )
            
            fig.update_yaxes(
                title_text="Bitcoin Price (USD)",
                title_font=dict(size=14, color=bitcoin_color),
                tickfont=dict(color=bitcoin_color),
                tickprefix="$",
                tickformat=",.0f",
                showline=True,
                linewidth=1,
                linecolor=bitcoin_color,
                secondary_y=True
            )
            
            # Save interactive HTML
            os.makedirs('figures/html', exist_ok=True)
            fig.write_html(f'figures/html/{safe_filename}_interactive.html')
            print(f"✅ Saved enhanced interactive visualization to figures/html/{safe_filename}_interactive.html")
            
        except Exception as e:
            print(f"⚠️ Could not create interactive visualization: {str(e)}")
            
        return True
    except Exception as e:
        print(f"❌ Error creating visualization: {str(e)}")
        return None

def plot_keyword_price_heatmap(top_n=10, save_fig=True, display_fig=False):
    """Create a heatmap showing correlations between keywords and Bitcoin price."""
    try:
        if not os.path.exists('data/keyword_trends.csv'):
            print("❌ No trend data found. Please run analyze_trends() first.")
            return None
        
        df = pd.read_csv('data/keyword_trends.csv')
        if 'correlation' not in df.columns:
            print("❌ No correlation data found in trends data.")
            return None
        
        # Sort by absolute correlation
        df['abs_corr'] = df['correlation'].abs()
        top_keywords = df.nlargest(top_n, 'abs_corr')['keyword'].tolist()
        corr_matrix = df[df['keyword'].isin(top_keywords)].set_index('keyword')['correlation']
        
        # Create improved figure with better styling
        plt.figure(figsize=(10, max(6, len(top_keywords) * 0.5)))
        
        # Create a custom colormap that is centered at zero
        # Blue for negative, Red/Orange for positive
        colors = ["#1E5AA8", "#4682B4", "#B8D0E5", "#F5F5F5", "#FFCC99", "#FF9933", "#E25822"]
        custom_cmap = sns.diverging_palette(220, 20, as_cmap=True)
        
        # Plot the heatmap with enhanced styling
        ax = sns.heatmap(
            corr_matrix.values.reshape(-1, 1), 
            annot=True, 
            yticklabels=corr_matrix.index, 
            xticklabels=['Price Correlation'], 
            cmap=custom_cmap, 
            center=0, 
            vmin=-1, 
            vmax=1, 
            fmt='.3f',
            annot_kws={"size": 12, "weight": "bold"},
            linewidths=0.5,
            cbar_kws={"shrink": 0.8, "label": "Correlation Coefficient"}
        )
        
        # Improve the title and labels
        plt.title('Keyword-Price Correlations', fontsize=18, fontweight='bold', pad=20)
        
        # Add subtitle with explanation
        plt.figtext(0.5, 0.01, 'Positive correlation: Keywords and price tend to move together\nNegative correlation: Keywords and price tend to move in opposite directions', 
                   ha='center', fontsize=10, fontstyle='italic')
        
        # Style improvements
        plt.ylabel('Keywords', fontsize=14, fontweight='bold')
        plt.yticks(fontsize=12)
        plt.xticks(fontsize=12, rotation=0)
        
        # Add a border around the heatmap
        for _, spine in ax.spines.items():
            spine.set_visible(True)
            spine.set_color('black')
            spine.set_linewidth(1)
            
        plt.tight_layout(rect=[0, 0.05, 1, 0.95])
        
        if save_fig:
            os.makedirs('figures', exist_ok=True)
            plt.savefig('figures/keyword_price_correlation.png', dpi=300, bbox_inches='tight')
            print("✅ Saved enhanced correlation heatmap to figures/keyword_price_correlation.png")
        
        if display_fig:
            plt.show()
        else:
            plt.close()
        
        # Create an interactive Plotly version with enhanced features
        try:
            # Prepare data for Plotly
            plot_df = corr_matrix.reset_index()
            plot_df.columns = ['keyword', 'correlation']
            plot_df = plot_df.sort_values('correlation')
            
            # Add frequency for bubble size if available
            if 'frequency' in df.columns:
                freq_data = df[df['keyword'].isin(top_keywords)].set_index('keyword')['frequency']
                plot_df = plot_df.merge(
                    freq_data.reset_index(), 
                    on='keyword', 
                    how='left'
                )
            else:
                plot_df['frequency'] = 10  # Default size
            
            # Create a more informative visualization
            if 'frequency' in plot_df.columns:
                # Create enhanced bubble chart
                fig = px.scatter(
                    plot_df, 
                    y='keyword', 
                    x='correlation', 
                    size='frequency',
                    color='correlation',
                    color_continuous_scale='RdBu_r',
                    range_color=[-1, 1],
                    title='Keyword Correlation with Bitcoin Price',
                    labels={
                        'correlation': 'Correlation Coefficient', 
                        'keyword': 'Keyword',
                        'frequency': 'Keyword Frequency'
                    },
                    hover_data={
                        'correlation': ':.3f',
                        'frequency': True
                    },
                    size_max=50
                )
            else:
                # Fallback to bar chart
                fig = px.bar(
                    plot_df, 
                    y='keyword', 
                    x='correlation', 
                    orientation='h',
                    color='correlation', 
                    color_continuous_scale='RdBu_r', 
                    range_color=[-1, 1],
                    title='Keyword Correlation with Bitcoin Price',
                    labels={
                        'correlation': 'Correlation Coefficient', 
                        'keyword': 'Keyword'
                    }
                )
            
            # Enhance layout        
            fig.update_layout(
                title={
                    'text': 'Keyword Correlation with Bitcoin Price',
                    'font': {'size': 24, 'color': '#333333'},
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                height=max(500, len(top_keywords) * 40),
                plot_bgcolor='rgba(245,245,245,0.95)',
                paper_bgcolor='rgba(250,250,250,0.95)',
                xaxis=dict(
                    title_font=dict(size=14),
                    tickfont=dict(size=12),
                    showgrid=True,
                    gridcolor='rgba(211,211,211,0.5)',
                    zeroline=True,
                    zerolinecolor='black',
                    zerolinewidth=1.5
                ),
                yaxis=dict(
                    title_font=dict(size=14),
                    tickfont=dict(size=12)
                ),
                coloraxis_colorbar=dict(
                    title='Correlation',
                    title_font=dict(size=12),
                    tickfont=dict(size=10)
                ),
                margin=dict(l=20, r=20, t=80, b=20)
            )
            
            # Add zero line
            fig.add_vline(x=0, line_dash='dash', line_color='gray', line_width=1.5)
            
            # Add annotations to explain correlation
            fig.add_annotation(
                xref='paper', yref='paper',
                x=0.01, y=1.07,
                text="<b>Negative Correlation</b>: Keywords and price move in opposite directions",
                showarrow=False,
                font=dict(size=10, color="#1E5AA8"),
                align="left"
            )
            
            fig.add_annotation(
                xref='paper', yref='paper',
                x=0.99, y=1.07,
                text="<b>Positive Correlation</b>: Keywords and price move together",
                showarrow=False,
                font=dict(size=10, color="#E25822"),
                align="right"
            )
            
            # Save enhanced interactive HTML
            os.makedirs('figures/html', exist_ok=True)
            fig.write_html('figures/html/keyword_correlation_interactive.html')
            print("✅ Saved enhanced interactive correlation visualization to figures/html/keyword_correlation_interactive.html")
            
        except Exception as e:
            print(f"⚠️ Could not create interactive correlation visualization: {str(e)}")
        
        return True
    except Exception as e:
        print(f"❌ Error creating heatmap: {str(e)}")
        return None

def generate_keyword_trend_dashboard():
    """Generate and open an interactive dashboard."""
    try:
        # Check if the dashboard script exists, otherwise use old implementation
        if os.path.exists('dashboard/dashboard.py'):
            # Call the dashboard script
            print("🔄 Generating interactive dashboard...")
            
            try:
                # Execute the dashboard script
                dashboard_dir = os.path.abspath('dashboard')
                result = subprocess.run([sys.executable, os.path.join(dashboard_dir, 'dashboard.py')], 
                                       capture_output=True, text=True)
                
                if result.returncode == 0:
                    # Dashboard generated successfully
                    dashboard_path = os.path.abspath('dashboard/index.html')
                    print(f"✅ Dashboard generated at {dashboard_path}")
                    
                    return dashboard_path
                else:
                    print(f"⚠️ Dashboard generation encountered issues: {result.stderr}")
                    return None
                    
            except Exception as e:
                print(f"⚠️ Error running dashboard script: {str(e)}")
                return None
        else:
            # Use simplified dashboard if the full dashboard script doesn't exist
            print("⚠️ Advanced dashboard not available. Using simplified dashboard.")
            return _generate_simple_dashboard()
    except Exception as e:
        print(f"❌ Error generating dashboard: {str(e)}")
        return None

def _generate_simple_dashboard():
    """Generate a simple dashboard using matplotlib (fallback option)."""
    try:
        # Create figures directory
        os.makedirs('figures', exist_ok=True)
        os.makedirs('dashboard', exist_ok=True)
        os.makedirs('dashboard/assets', exist_ok=True)
        
        # Create keyword correlations
        plot_keyword_price_heatmap(save_fig=True, display_fig=False)
        
        # Plot top keywords
        top_keywords = []
        if os.path.exists('data/keyword_trends.csv'):
            trends = pd.read_csv('data/keyword_trends.csv')
            top_keywords = trends.nlargest(5, 'frequency')['keyword'].tolist()
            for keyword in top_keywords:
                plot_keyword_vs_price(keyword, save_fig=True, display_fig=False)
        
        # Copy necessary image files to dashboard assets
        try:
            # Copy main correlation heatmap
            shutil.copy('figures/keyword_price_correlation.png', 'dashboard/assets/')
            
            # Copy keyword charts
            for keyword in top_keywords:
                safe_name = sanitize_filename(keyword)
                if os.path.exists(f'figures/{safe_name}_vs_price.png'):
                    shutil.copy(f'figures/{safe_name}_vs_price.png', 'dashboard/assets/')
            
            # Copy Granger causality results if available
            if os.path.exists('figures/granger_causality_tests.png'):
                shutil.copy('figures/granger_causality_tests.png', 'dashboard/assets/')
        except Exception as e:
            print(f"⚠️ Warning: Could not copy some image files: {str(e)}")
        
        # Add price data for summary stats
        price_stats = {}
        real_price_data = False
        
        # Try to get current price data first
        if os.path.exists('data/current_price.json'):
            try:
                with open('data/current_price.json', 'r') as f:
                    current_data = json.load(f)
                    
                # Check if the file was modified in the last 24 hours
                file_age = time.time() - os.path.getmtime('data/current_price.json')
                if file_age < 24 * 60 * 60:  # Less than 24 hours old
                    price_stats = {
                        'current': f"${current_data['price']:,.2f}",
                        'market_cap': f"${current_data['market_cap'] / 1_000_000_000:.2f}B",
                        'change_24h': f"{current_data['change_24h']:.2f}%",
                        'volume': f"${current_data['vol_24h'] / 1_000_000_000:.2f}B"
                    }
                    real_price_data = True
            except Exception as e:
                print(f"⚠️ Could not read current price data: {str(e)}")
        
        # Fall back to historical price data if no current data
        if not real_price_data and os.path.exists('data/bitcoin_prices.csv'):
            try:
                price_df = pd.read_csv('data/bitcoin_prices.csv')
                if 'price' in price_df.columns:
                    price_stats = {
                        'current': f"${price_df['price'].iloc[-1]:,.2f}",
                        'min': f"${price_df['price'].min():,.2f}",
                        'max': f"${price_df['price'].max():,.2f}",
                        'change': f"{((price_df['price'].iloc[-1] / price_df['price'].iloc[0]) - 1) * 100:.1f}%"
                    }
            except Exception as e:
                print(f"⚠️ Could not calculate price statistics: {str(e)}")
                
        # Add summary statistics if available
        if price_stats:
            html = f"""<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Bitcoin News Keyword Analysis</title>
                <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
                <style>
                    :root {{
                        --primary-color: #f2a900;
                        --secondary-color: #4d4d4d;
                        --background-color: #f9f9f9;
                        --card-bg: #ffffff;
                        --text-color: #333333;
                        --border-color: #e0e0e0;
                    }}
                    
                    * {{
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }}
                    
                    body {{
                        font-family: 'Roboto', sans-serif;
                        line-height: 1.6;
                        color: var(--text-color);
                        background-color: var(--background-color);
                        padding: 0;
                    }}
                    
                    .container {{
                        max-width: 1200px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    
                    header {{
                        background: linear-gradient(135deg, var(--primary-color), #f78100);
                        color: white;
                        padding: 2rem;
                        text-align: center;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    }}
                    
                    h1 {{
                        font-size: 2.5rem;
                        margin-bottom: 0.5rem;
                    }}
                    
                    h2 {{
                        color: var(--primary-color);
                        margin: 1.5rem 0 1rem;
                        border-bottom: 2px solid var(--primary-color);
                        padding-bottom: 0.5rem;
                    }}
                    
                    h3 {{
                        color: var(--secondary-color);
                        margin: 1rem 0;
                    }}
                    
                    .subtitle {{
                        font-weight: 300;
                        color: rgba(255,255,255,0.9);
                    }}
                    
                    .timestamp {{
                        background-color: rgba(0,0,0,0.1);
                        padding: 0.5rem 1rem;
                        border-radius: 20px;
                        display: inline-block;
                        margin-top: 1rem;
                        font-size: 0.9rem;
                    }}
                    
                    .card {{
                        background-color: var(--card-bg);
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        padding: 1.5rem;
                        margin-bottom: 2rem;
                        transition: transform 0.3s ease, box-shadow 0.3s ease;
                    }}
                    
                    .card:hover {{
                        transform: translateY(-5px);
                        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
                    }}
                    
                    .stats-row {{
                        display: flex;
                        flex-wrap: wrap;
                        gap: 15px;
                        margin-bottom: 1.5rem;
                    }}
                    
                    .stat-card {{
                        flex: 1;
                        min-width: 150px;
                        background-color: var(--card-bg);
                        border-radius: 8px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        padding: 1rem;
                        text-align: center;
                        border-left: 4px solid var(--primary-color);
                    }}
                    
                    .stat-title {{
                        font-size: 0.9rem;
                        color: var(--secondary-color);
                        margin-bottom: 0.5rem;
                    }}
                    
                    .stat-value {{
                        font-size: 1.4rem;
                        font-weight: 700;
                        color: var(--primary-color);
                    }}
                    
                    .flex-container {{
                        display: flex;
                        flex-wrap: wrap;
                        gap: 20px;
                    }}
                    
                    .correlation-card {{
                        flex: 1 1 100%;
                    }}
                    
                    .keyword-card {{
                        flex: 1 1 calc(50% - 20px);
                        min-width: 300px;
                    }}
                    
                    img {{
                        max-width: 100%;
                        height: auto;
                        border-radius: 4px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                        margin: 0.5rem 0;
                    }}
                    
                    .footer {{
                        text-align: center;
                        padding: 2rem;
                        color: var(--secondary-color);
                        font-size: 0.9rem;
                        border-top: 1px solid var(--border-color);
                        margin-top: 2rem;
                    }}
                    
                    .bitcoin-logo {{
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
                    }}
                    
                    .disclaimer {{
                        background-color: rgba(255, 248, 225, 0.9);
                        border-left: 4px solid #ffc107;
                        padding: 10px 15px;
                        margin: 15px 0;
                        border-radius: 4px;
                        font-size: 0.9rem;
                        color: #856404;
                    }}
                    
                    @media (max-width: 768px) {{
                        .keyword-card {{
                            flex: 1 1 100%;
                        }}
                        h1 {{
                            font-size: 2rem;
                        }}
                    }}
                </style>
            </head>
            <body>
                <header>
                    <div class="container">
                        <h1><span class="bitcoin-logo">&#8383;</span> Bitcoin News Keyword Analysis</h1>
                        <p class="subtitle">Analyzing Cryptocurrency News Keywords and Price Correlations</p>
                        <div class="timestamp">Generated on {pd.Timestamp.now().strftime('%B %d, %Y at %H:%M:%S')}</div>
                    </div>
                </header>
                
                <div class="container">
                    <div class="disclaimer">
                        <strong>Note:</strong> This dashboard uses sample/demonstration data for Bitcoin prices and news articles. 
                        The price information shown is not real-time market data.
                    </div>
            """
            
            # Display different stats based on whether we have real or sample data
            if real_price_data:
                html += f"""
                        <div class="card">
                            <h2>Bitcoin Price Overview {'' if real_price_data else '<span style="font-size: 0.8rem; color: #856404; background-color: #fff3cd; padding: 3px 8px; border-radius: 12px; margin-left: 10px; vertical-align: middle;">Sample Data</span>'}</h2>
                            <div class="stats-row">
                                <div class="stat-card">
                                    <div class="stat-title">Current Price</div>
                                    <div class="stat-value">{price_stats.get('current', 'N/A')}</div>
                                </div>
                                <div class="stat-card">
                                    <div class="stat-title">24h Change</div>
                                    <div class="stat-value">{price_stats.get('change_24h', 'N/A')}</div>
                                </div>
                                <div class="stat-card">
                                    <div class="stat-title">Market Cap</div>
                                    <div class="stat-value">{price_stats.get('market_cap', 'N/A')}</div>
                                </div>
                                <div class="stat-card">
                                    <div class="stat-title">24h Volume</div>
                                    <div class="stat-value">{price_stats.get('volume', 'N/A')}</div>
                                </div>
                    """
            else:
                html += f"""
                        <div class="card">
                            <h2>Bitcoin Price Overview {'' if real_price_data else '<span style="font-size: 0.8rem; color: #856404; background-color: #fff3cd; padding: 3px 8px; border-radius: 12px; margin-left: 10px; vertical-align: middle;">Sample Data</span>'}</h2>
                            <div class="stats-row">
                                <div class="stat-card">
                                    <div class="stat-title">Current Price</div>
                                    <div class="stat-value">{price_stats.get('current', 'N/A')}</div>
                                </div>
                                <div class="stat-card">
                                    <div class="stat-title">Price Change</div>
                                    <div class="stat-value">{price_stats.get('change', 'N/A')}</div>
                                </div>
                                <div class="stat-card">
                                    <div class="stat-title">Period Low</div>
                                    <div class="stat-value">{price_stats.get('min', 'N/A')}</div>
                                </div>
                                <div class="stat-card">
                                    <div class="stat-title">Period High</div>
                                    <div class="stat-value">{price_stats.get('max', 'N/A')}</div>
                                </div>
                    """
            
            html += """
                    </div>
                </div>
            """
            
            # Add keyword count statistics
            html += """
                    <div class="card correlation-card">
                        <h2>Keyword-Price Correlations</h2>
                        <p>This heatmap shows how different keywords in news correlate with Bitcoin price movements.</p>
                        <img src="assets/keyword_price_correlation.png" alt="Keyword Correlations">
                    </div>
                    
                    <h2>Keyword Trend Analysis</h2>
                    <div class="flex-container">
            """
            
            # Add keyword charts
            if top_keywords:
                for keyword in top_keywords:
                    safe_name = sanitize_filename(keyword)
                    html += f"""
                        <div class="card keyword-card">
                            <h3>'{keyword}' Trend Analysis</h3>
                            <img src="assets/{safe_name}_vs_price.png" alt="{keyword} vs Price">
                        </div>
                    """
                    
            # Add Granger causality results if available
            if os.path.exists('figures/granger_causality_tests.png'):
                html += """
                    </div>
                    
                    <div class="card">
                        <h2>Granger Causality Test Results</h2>
                        <p>Granger causality tests determine if one time series can predict another.</p>
                        <img src="assets/granger_causality_tests.png" alt="Granger Causality Tests">
                    </div>
                """
            else:
                html += """
                    </div>
                """
                
            # Close HTML
            html += """
                    <div class="footer">
                        <p>Created with TextBlob, Matplotlib, and Python | Bitcoin News Keyword Analysis | Data Analysis Project</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Save HTML dashboard both in figures/ and dashboard/ directories
            with open('dashboard/index.html', 'w') as f:
                f.write(html)
            
            dashboard_path = os.path.abspath('dashboard/index.html')
            print(f"✅ Enhanced dashboard generated at {dashboard_path}")
            
            return dashboard_path
            
    except Exception as e:
        print(f"❌ Error generating enhanced dashboard: {str(e)}")
        return None

if __name__ == "__main__":
    # Test the functions
    plot_keyword_vs_price("bitcoin")
    plot_keyword_price_heatmap()
    generate_keyword_trend_dashboard()
