import pandas as pd
import os
import numpy as np
import warnings
from datetime import datetime, timedelta

def analyze_trends(time_window='daily', min_freq=2):
    """
    Analyze keyword trends and their correlation with Bitcoin prices.
    
    Args:
        time_window (str): Time window for analysis ('daily' or 'hourly')
        min_freq (int): Minimum keyword frequency to include
        
    Returns:
        pandas.DataFrame: DataFrame with trend analysis results
    """
    try:
        # Load data
        if not os.path.exists('data/bitcoin_news_with_keywords.csv'):
            print("❌ No keyword data found. Please extract keywords first.")
            return None
            
        if not os.path.exists('data/bitcoin_prices.csv'):
            print("❌ No price data found. Please fetch price data first.")
            return None
            
        # Read data
        news_df = pd.read_csv('data/bitcoin_news_with_keywords.csv')
        prices_df = pd.read_csv('data/bitcoin_prices.csv')
        
        # Convert date columns to datetime
        news_df['date'] = pd.to_datetime(news_df['date'])
        prices_df['date'] = pd.to_datetime(prices_df['date'])
        
        # Convert keywords from string to list
        news_df['keywords'] = news_df['keywords'].apply(eval)
        
        # Flatten news data to (date, keyword) pairs
        records = []
        for _, row in news_df.iterrows():
            for kw in row['keywords']:
                records.append({'date': row['date'], 'keyword': kw})
        flat_df = pd.DataFrame(records)
        
        # Aggregate keyword counts per day
        keyword_daily = flat_df.groupby(['keyword', 'date']).size().reset_index(name='count')
        
        # Print keyword stats before filtering
        print("\n[DEBUG] Keyword stats before filtering:")
        keyword_stats = keyword_daily.groupby('keyword').agg(
            total_mentions=('count', 'sum'),
            unique_days=('date', 'nunique')
        ).sort_values('total_mentions', ascending=False)
        print(keyword_stats.head(20))
        print(f"Total unique keywords: {len(keyword_stats)}")
        
        # Merge with price data
        merged = pd.merge(keyword_daily, prices_df[['date', 'price']], on='date', how='inner')
        print("\n[DEBUG] Sample of merged data:")
        print(merged.head(10))
        print(f"Total merged rows: {len(merged)}")
        
        # Only keep keywords with enough data points
        keyword_counts = merged['keyword'].value_counts()
        valid_keywords = keyword_counts[keyword_counts >= min_freq].index.tolist()
        merged = merged[merged['keyword'].isin(valid_keywords)]
        
        # Calculate correlation for each keyword
        trend_data = []
        for kw in valid_keywords:
            sub = merged[merged['keyword'] == kw]
            if len(sub) < 3:
                continue
            corr = sub['count'].corr(sub['price'])
            trend_data.append({
                'keyword': kw,
                'frequency': sub['count'].sum(),
                'correlation': corr,
                'max_count': sub['count'].max(),
                'avg_count': sub['count'].mean()
            })
        
        trend_df = pd.DataFrame(trend_data)
        if trend_df.empty:
            print("❌ No trends found with the given parameters")
            return None
        trend_df = trend_df.sort_values('frequency', ascending=False)
        
        # Save merged data for visualization
        merged = merged.rename(columns={'date': 'time_window'})
        merged.to_csv('data/merged_keyword_price.csv', index=False)
        trend_df.to_csv('data/keyword_trends.csv', index=False)
        print(f"✅ Successfully analyzed trends for {len(trend_df)} keywords")
        return trend_df
    except Exception as e:
        print(f"❌ Error analyzing trends: {str(e)}")
        return None

if __name__ == "__main__":
    analyze_trends()