import os
import sys
import time
from visualize import plot_keyword_vs_price, plot_keyword_price_heatmap, generate_keyword_trend_dashboard

def main():
    """
    Generate visualizations and dashboard without the problematic trends overview.
    """
    # Ensure directories exist
    os.makedirs('figures', exist_ok=True)
    os.makedirs('figures/html', exist_ok=True)
    os.makedirs('dashboard', exist_ok=True)
    os.makedirs('dashboard/assets', exist_ok=True)
    
    # Clean up any existing trends overview files
    trend_files = [
        'figures/keyword_trends_overview.png',
        'figures/html/keyword_trends_overview.html',
        'dashboard/assets/keyword_trends_overview.png'
    ]
    
    for file_path in trend_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Removed {file_path}")
            except Exception as e:
                print(f"Could not remove {file_path}: {e}")
    
    # Load keyword trends
    if os.path.exists('data/keyword_trends.csv'):
        import pandas as pd
        trend_data = pd.read_csv('data/keyword_trends.csv')
        top_keywords = trend_data.nlargest(3, 'frequency')['keyword'].tolist()
        print(f"Top keywords: {', '.join(top_keywords)}")
    else:
        top_keywords = ['bitcoin', 'price', 'market']
        print("Using default keywords")
    
    # Generate correlation heatmap
    print("Creating correlation heatmap...")
    plot_keyword_price_heatmap(
        top_n=5, 
        save_fig=True,
        display_fig=False
    )
    
    # Generate individual keyword charts
    for keyword in top_keywords:
        print(f"Creating visualization for '{keyword}'...")
        plot_keyword_vs_price(
            keyword,
            save_fig=True,
            display_fig=False
        )
        time.sleep(0.5)
    
    # Generate dashboard without opening it
    print("Generating dashboard...")
    dashboard_path = generate_keyword_trend_dashboard()
    
    # Open dashboard once
    if dashboard_path:
        try:
            print(f"Opening dashboard at {dashboard_path}")
            
            # Use a single method to open the dashboard
            import webbrowser
            webbrowser.open(f'file:///{os.path.abspath(dashboard_path)}')
            
        except Exception as e:
            print(f"Could not open dashboard: {e}")
            print(f"Please open manually: {os.path.abspath(dashboard_path)}")

if __name__ == "__main__":
    main() 