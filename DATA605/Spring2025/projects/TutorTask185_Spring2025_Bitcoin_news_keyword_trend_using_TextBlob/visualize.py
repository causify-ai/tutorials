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
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove any leading/trailing spaces and periods
    sanitized = sanitized.strip('. ')
    # Replace multiple underscores with a single one
    sanitized = re.sub(r'_+', '_', sanitized)
    # Ensure the filename is not empty
    if not sanitized:
        sanitized = "unnamed"
    return sanitized

def plot_keyword_vs_price(keyword, save_fig=True, display_fig=DEFAULT_DISPLAY):
    try:
        if not os.path.exists('data/merged_keyword_price.csv'):
            print("❌ No merged data found. Please run analyze_trends() first.")
            return None
        df = pd.read_csv('data/merged_keyword_price.csv')
        keyword_data = df[df['keyword'] == keyword]
        if keyword_data.empty:
            print(f"❌ No data found for keyword '{keyword}'")
            return None
        plt.figure(figsize=(12, 6))
        ax1 = plt.gca()
        ax2 = ax1.twinx()
        ax1.plot(pd.to_datetime(keyword_data['time_window']), keyword_data['count'], color='blue', marker='o', label='Keyword Frequency')
        ax2.plot(pd.to_datetime(keyword_data['time_window']), keyword_data['price'], color='orange', marker='s', label='Bitcoin Price')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Keyword Frequency', color='blue')
        ax2.set_ylabel('Bitcoin Price (USD)', color='orange')
        plt.title(f"'{keyword}' Frequency vs Bitcoin Price")
        plt.xticks(rotation=45)
        plt.tight_layout()
        if save_fig:
            os.makedirs('figures', exist_ok=True)
            safe_filename = sanitize_filename(keyword)
            plt.savefig(f'figures/{safe_filename}_vs_price.png')
            print(f"✅ Saved visualization to figures/{safe_filename}_vs_price.png")
        if display_fig:
            plt.show()
        else:
            plt.close()
        return True
    except Exception as e:
        print(f"❌ Error creating visualization: {str(e)}")
        return None

def plot_keyword_price_heatmap(top_n=10, save_fig=True, display_fig=DEFAULT_DISPLAY):
    try:
        if not os.path.exists('data/keyword_trends.csv'):
            print("❌ No trend data found. Please run analyze_trends() first.")
            return None
        df = pd.read_csv('data/keyword_trends.csv')
        top_keywords = df.nlargest(top_n, 'frequency')['keyword'].tolist()
        corr_matrix = df[df['keyword'].isin(top_keywords)].set_index('keyword')['correlation']
        plt.figure(figsize=(8, max(4, len(top_keywords) * 0.5)))
        sns.heatmap(corr_matrix.values.reshape(-1, 1), annot=True, yticklabels=corr_matrix.index, xticklabels=['Correlation'], cmap='RdBu', center=0)
        plt.title('Keyword-Price Correlations')
        plt.ylabel('Keywords')
        plt.tight_layout()
        if save_fig:
            os.makedirs('figures', exist_ok=True)
            plt.savefig('figures/keyword_price_correlation.png')
            print("✅ Saved visualization to figures/keyword_price_correlation.png")
        if display_fig:
            plt.show()
        else:
            plt.close()
        return True
    except Exception as e:
        print(f"❌ Error creating heatmap: {str(e)}")
        return None

def generate_keyword_trend_dashboard():
    print("[INFO] Dashboard not implemented for matplotlib version.")
    return None

if __name__ == "__main__":
    # Test the functions
    plot_keyword_vs_price("bitcoin")
    plot_keyword_price_heatmap()
    generate_keyword_trend_dashboard()
