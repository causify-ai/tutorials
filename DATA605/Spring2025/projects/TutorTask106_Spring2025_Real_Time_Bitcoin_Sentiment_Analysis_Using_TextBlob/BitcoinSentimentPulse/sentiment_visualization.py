"""
Sentiment Visualization Module

This module provides visualization tools for Bitcoin sentiment analysis data,
including sentiment trends, distributions, and news samples.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from datetime import datetime, timedelta

def load_sentiment_data(frequency='daily', days=7):
    """
    Load sentiment data from files based on frequency.
    
    Args:
        frequency: 'hourly' or 'daily'
        days: Number of days to retrieve
    
    Returns:
        pd.DataFrame: DataFrame with sentiment data
    """
    file_path = f'data/{frequency}_sentiment.csv'
    try:
        # Handle different date formats between hourly and daily data
        try:
            # First try with automatic parsing
            df = pd.read_csv(file_path, parse_dates=['date'])
            
            # If the date is still a string, try with specific format
            if pd.api.types.is_string_dtype(df['date']):
                if frequency == 'hourly':
                    # For hourly data format is usually YYYY-MM-DD
                    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
                else:
                    # For daily data try more general parsing
                    df['date'] = pd.to_datetime(df['date'], errors='coerce')
        except Exception as e:
            # If specific parsing fails, use a more flexible approach
            df = pd.read_csv(file_path)
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        
        # Filter for specified number of days
        if days > 0:
            cutoff_date = datetime.now() - timedelta(days=days)
            # Make sure no NaT values in date column
            df = df.dropna(subset=['date'])
            df = df[df['date'] >= cutoff_date]
            
        return df
    except Exception as e:
        st.error(f"Error loading {frequency} sentiment data: {str(e)}")
        return pd.DataFrame()

def load_latest_sentiment_info():
    """
    Load the latest sentiment summary info with article examples.
    
    Returns:
        dict: Dictionary with sentiment summary
    """
    import json
    import os
    
    if os.path.exists('data/latest_sentiment.json'):
        try:
            with open('data/latest_sentiment.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error loading latest sentiment data: {str(e)}")
    
    return {}

def plot_sentiment_trend(sentiment_df, bitcoin_price_df=None):
    """
    Plot sentiment trend over time, with optional Bitcoin price overlay.
    
    Args:
        sentiment_df: DataFrame with sentiment data
        bitcoin_price_df: Optional DataFrame with Bitcoin price data
    
    Returns:
        go.Figure: Plotly figure with sentiment trend
    """
    if sentiment_df.empty:
        return None
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add sentiment polarity trace
    fig.add_trace(
        go.Scatter(
            x=sentiment_df['date'],
            y=sentiment_df['avg_polarity'],
            name="Sentiment Polarity",
            line=dict(color='#1f77b4', width=2),
            mode='lines+markers'
        ),
        secondary_y=False,
    )
    
    # Add shaded area for subjectivity
    fig.add_trace(
        go.Scatter(
            x=sentiment_df['date'],
            y=sentiment_df['avg_subjectivity'],
            name="Subjectivity",
            line=dict(color='rgba(255, 165, 0, 0.5)', width=1),
            fill='tozeroy'
        ),
        secondary_y=False,
    )
    
    # Add Bitcoin price if provided
    if bitcoin_price_df is not None and not bitcoin_price_df.empty:
        # Ensure dates match up
        common_dates = []
        price_values = []
        
        for date in sentiment_df['date']:
            date_str = date.strftime('%Y-%m-%d')
            for price_date in bitcoin_price_df.index:
                price_date_str = price_date.strftime('%Y-%m-%d')
                if price_date_str == date_str:
                    common_dates.append(date)
                    # Handle different column names from different data sources
                    if 'Close' in bitcoin_price_df.columns:
                        price_values.append(bitcoin_price_df.loc[price_date, 'Close'])
                    elif 'price' in bitcoin_price_df.columns:
                        price_values.append(bitcoin_price_df.loc[price_date, 'price'])
                    break
        
        if common_dates and price_values:
            fig.add_trace(
                go.Scatter(
                    x=common_dates,
                    y=price_values,
                    name="Bitcoin Price (USD)",
                    line=dict(color='#2ca02c', width=2, dash='dot'),
                    mode='lines'
                ),
                secondary_y=True,
            )
    
    # Add a horizontal line at y=0 for polarity reference
    fig.add_shape(
        type="line",
        x0=sentiment_df['date'].min(),
        y0=0,
        x1=sentiment_df['date'].max(),
        y1=0,
        line=dict(color="rgba(0, 0, 0, 0.3)", width=1, dash="dash"),
    )
    
    # Set titles and labels
    fig.update_layout(
        title="Bitcoin News Sentiment Trend Over Time",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    
    fig.update_yaxes(title_text="Sentiment (Polarity & Subjectivity)", secondary_y=False)
    
    if bitcoin_price_df is not None and not bitcoin_price_df.empty:
        fig.update_yaxes(title_text="Bitcoin Price (USD)", secondary_y=True)
    
    return fig

def plot_sentiment_distribution(sentiment_df):
    """
    Plot sentiment polarity distribution.
    
    Args:
        sentiment_df: DataFrame with sentiment data
    
    Returns:
        go.Figure: Plotly figure with sentiment distribution
    """
    if sentiment_df.empty:
        return None
    
    # Create histogram for polarity
    fig = go.Figure()
    
    fig.add_trace(
        go.Histogram(
            x=sentiment_df['avg_polarity'],
            histnorm='probability density',
            nbinsx=20,
            marker_color='#1f77b4',
            opacity=0.7,
            name="Polarity Distribution"
        )
    )
    
    # Add KDE curve
    from scipy import stats
    kde_x = np.linspace(
        sentiment_df['avg_polarity'].min(), 
        sentiment_df['avg_polarity'].max(), 
        100
    )
    kde = stats.gaussian_kde(sentiment_df['avg_polarity'].dropna())
    kde_y = kde(kde_x)
    
    fig.add_trace(
        go.Scatter(
            x=kde_x,
            y=kde_y,
            mode='lines',
            line=dict(color='crimson', width=2),
            name="Density"
        )
    )
    
    # Add median line
    median = sentiment_df['avg_polarity'].median()
    fig.add_shape(
        type="line",
        x0=median,
        y0=0,
        x1=median,
        y1=max(kde_y) * 1.1,
        line=dict(color="green", width=2, dash="dash"),
    )
    
    # Add annotation for median
    fig.add_annotation(
        x=median,
        y=max(kde_y) * 1.1,
        text=f"Median: {median:.3f}",
        showarrow=True,
        arrowhead=1,
        ax=0,
        ay=-40
    )
    
    # Set titles and layout
    fig.update_layout(
        title="Bitcoin News Sentiment Distribution",
        xaxis_title="Sentiment Polarity",
        yaxis_title="Density",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    
    return fig

def plot_sentiment_by_source(sentiment_info):
    """
    Plot sentiment breakdown by news source.
    
    Args:
        sentiment_info: Dictionary with sentiment analysis results
    
    Returns:
        go.Figure: Plotly figure with sentiment by source
    """
    if not sentiment_info or 'articles' not in sentiment_info:
        return None
    
    # Extract source and sentiment from articles
    sources = []
    polarities = []
    
    for article in sentiment_info['articles']:
        if 'source' in article and 'sentiment' in article:
            # Extract source name
            source = article['source'].get('name', 'Unknown')
            polarity = article['sentiment'].get('polarity', 0)
            
            sources.append(source)
            polarities.append(polarity)
    
    # Create DataFrame
    df = pd.DataFrame({'source': sources, 'polarity': polarities})
    
    # Aggregate by source (mean polarity)
    source_sentiment = df.groupby('source')['polarity'].mean().reset_index()
    source_sentiment = source_sentiment.sort_values('polarity')
    
    # Create bar chart
    fig = px.bar(
        source_sentiment,
        x='source',
        y='polarity',
        color='polarity',
        color_continuous_scale='RdYlGn',
        title="Bitcoin Sentiment by News Source",
        labels={'polarity': 'Avg. Sentiment Polarity', 'source': 'News Source'}
    )
    
    # Update layout
    fig.update_layout(
        xaxis_tickangle=-45,
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    
    return fig

def sentiment_price_correlation(sentiment_df, bitcoin_price_df):
    """
    Calculate and display correlation between sentiment and price movement.
    
    Args:
        sentiment_df: DataFrame with sentiment data
        bitcoin_price_df: DataFrame with Bitcoin price data
    
    Returns:
        float: Correlation coefficient
        go.Figure: Scatter plot showing relationship
    """
    if sentiment_df.empty or bitcoin_price_df.empty:
        return None, None
    
    # Create a copy to avoid modifying the original
    try:    
        price_df = bitcoin_price_df.copy()
        
        # Determine the price column name
        price_col = None
        if 'price' in price_df.columns:
            price_col = 'price'
        elif 'Close' in price_df.columns:
            # Rename 'Close' to 'price' for consistency
            price_df.rename(columns={'Close': 'price'}, inplace=True)
            price_col = 'price'
        else:
            # Try to find any numeric column as fallback
            for col in price_df.columns:
                if pd.api.types.is_numeric_dtype(price_df[col]):
                    price_df.rename(columns={col: 'price'}, inplace=True)
                    price_col = 'price'
                    break
        
        # If we still don't have a price column, return
        if price_col is None:
            st.warning("Cannot find price data column in the Bitcoin price data")
            return None, None
        
        # Prepare data
        data = []
        
        for idx, row in sentiment_df.iterrows():
            # Ensure date is datetime
            if isinstance(row['date'], str):
                date = pd.to_datetime(row['date'])
            else:
                date = row['date']
                
            date_str = date.strftime('%Y-%m-%d')
            
            # Try to match with price data
            for price_date in price_df.index:
                try:
                    # Handle different index types
                    if isinstance(price_date, str):
                        price_date_str = price_date
                    else:
                        price_date_str = price_date.strftime('%Y-%m-%d')
                        
                    if price_date_str == date_str:
                        # Get next day's price if available for price change
                        next_day_idx = price_df.index.get_loc(price_date) + 1
                        
                        if next_day_idx < len(price_df):
                            next_day_price = price_df.iloc[next_day_idx]['price']
                            current_price = price_df.loc[price_date, 'price']
                            price_change_pct = (next_day_price - current_price) / current_price * 100
                            
                            data.append({
                                'date': date,
                                'sentiment': row['avg_polarity'],
                                'price_change_pct': price_change_pct
                            })
                        break
                except (TypeError, AttributeError, ValueError) as e:
                    # Skip any problematic date entries
                    continue
    except Exception as e:
        st.error(f"Error processing price data: {str(e)}")
        return None, None
    
    try:
        # Create DataFrame
        df = pd.DataFrame(data)
        
        if len(df) < 2:
            return None, None
        
        # Calculate correlation
        correlation = df['sentiment'].corr(df['price_change_pct'])
    except Exception as e:
        st.error(f"Error calculating correlation: {str(e)}")
        return None, None
    
    # Create scatter plot
    fig = px.scatter(
        df,
        x='sentiment',
        y='price_change_pct',
        trendline='ols',
        hover_data=['date'],
        title=f"Sentiment vs Next-Day Price Change (Correlation: {correlation:.3f})",
        labels={
            'sentiment': 'Sentiment Polarity',
            'price_change_pct': 'Next-Day Price Change (%)',
            'date': 'Date'
        }
    )
    
    # Update layout
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
    )
    
    return correlation, fig

def display_sentiment_dashboard(bitcoin_price_df=None):
    """
    Display comprehensive sentiment analysis dashboard.
    
    Args:
        bitcoin_price_df: Optional DataFrame with Bitcoin price data
    """
    st.header("Bitcoin News Sentiment Analysis")
    
    # Add frequency selection
    sentiment_frequency = st.radio(
        "Select Sentiment Analysis Frequency",
        ["Hourly", "Daily"],
        horizontal=True,
        index=0
    )
    
    # Time period selection
    if sentiment_frequency == "Hourly":
        days_options = [1, 2, 3, 7]
        default_days = 1
    else:
        days_options = [7, 14, 30, 90]
        default_days = 7
    
    days = st.select_slider(
        f"Select {sentiment_frequency} Data Period",
        options=days_options,
        value=default_days
    )
    
    # Load sentiment data
    frequency = sentiment_frequency.lower()
    sentiment_df = load_sentiment_data(frequency=frequency, days=days)
    
    # Load latest sentiment info for article examples
    latest_sentiment = load_latest_sentiment_info()
    
    # Create tabs for different visualizations
    tab1, tab2, tab3, tab4 = st.tabs([
        "Sentiment Trend", 
        "Sentiment Distribution", 
        "News Sources", 
        "Market Impact"
    ])
    
    with tab1:
        if sentiment_df.empty:
            st.warning(f"No {sentiment_frequency.lower()} sentiment data available for the selected period.")
        else:
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            
            avg_polarity = sentiment_df['avg_polarity'].mean()
            polarity_color = "green" if avg_polarity > 0 else "red"
            
            with col1:
                st.metric(
                    "Average Sentiment", 
                    f"{avg_polarity:.3f}", 
                    delta=None
                )
            
            with col2:
                # Calculate 24h change for hourly or 7d change for daily
                if len(sentiment_df) > 1:
                    if frequency == "hourly":
                        lookback = min(24, len(sentiment_df) - 1)
                    else:
                        lookback = min(7, len(sentiment_df) - 1)
                    
                    current = sentiment_df['avg_polarity'].iloc[-1]
                    previous = sentiment_df['avg_polarity'].iloc[-lookback-1]
                    change = current - previous
                    st.metric(
                        f"Sentiment Change ({lookback}{'h' if frequency == 'hourly' else 'd'})",
                        f"{current:.3f}",
                        f"{change:.3f}"
                    )
                else:
                    st.metric("Current Sentiment", f"{sentiment_df['avg_polarity'].iloc[0]:.3f}", delta=None)
            
            with col3:
                # Calculate article count
                total_articles = sentiment_df['article_count'].sum()
                st.metric("Total Articles Analyzed", f"{total_articles}")
            
            # Sentiment trend chart
            fig = plot_sentiment_trend(sentiment_df, bitcoin_price_df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        if sentiment_df.empty:
            st.warning(f"No {sentiment_frequency.lower()} sentiment data available for the selected period.")
        else:
            # Sentiment distribution
            fig = plot_sentiment_distribution(sentiment_df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            # Sentiment value ranges
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Positive Articles", f"{(sentiment_df['avg_polarity'] > 0.05).sum()} ({(sentiment_df['avg_polarity'] > 0.05).mean()*100:.1f}%)")
            with col2:
                st.metric("Neutral Articles", f"{((sentiment_df['avg_polarity'] >= -0.05) & (sentiment_df['avg_polarity'] <= 0.05)).sum()} ({((sentiment_df['avg_polarity'] >= -0.05) & (sentiment_df['avg_polarity'] <= 0.05)).mean()*100:.1f}%)")
            with col3:
                st.metric("Negative Articles", f"{(sentiment_df['avg_polarity'] < -0.05).sum()} ({(sentiment_df['avg_polarity'] < -0.05).mean()*100:.1f}%)")
    
    with tab3:
        # Display sentiment by news source
        fig = plot_sentiment_by_source(latest_sentiment)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No source breakdown available in the latest sentiment data.")
    
    with tab4:
        if bitcoin_price_df is not None and not sentiment_df.empty:
            # Correlation analysis
            correlation, fig = sentiment_price_correlation(sentiment_df, bitcoin_price_df)
            
            if correlation is not None and fig is not None:
                # Correlation strength descriptor
                if abs(correlation) < 0.2:
                    corr_desc = "very weak"
                elif abs(correlation) < 0.4:
                    corr_desc = "weak"
                elif abs(correlation) < 0.6:
                    corr_desc = "moderate"
                elif abs(correlation) < 0.8:
                    corr_desc = "strong"
                else:
                    corr_desc = "very strong"
                
                # Correlation direction
                direction = "positive" if correlation > 0 else "negative"
                
                st.info(f"The sentiment analysis shows a {corr_desc} {direction} correlation ({correlation:.3f}) with next-day Bitcoin price movements in the selected period.")
                
                st.plotly_chart(fig, use_container_width=True)
                
                if correlation > 0.3:
                    st.success("This positive correlation suggests that higher sentiment values tend to precede price increases.")
                elif correlation < -0.3:
                    st.success("This negative correlation suggests that lower sentiment values tend to precede price increases, possibly indicating contrarian market behavior.")
                else:
                    st.info("The correlation is not strong enough to draw definitive conclusions about the predictive power of sentiment in this period.")
            else:
                st.warning("Insufficient data to calculate sentiment-price correlation.")
        else:
            st.warning("Bitcoin price data is required to analyze sentiment impact on market.")

def display_news_examples(latest_sentiment):
    """
    Display examples of recent news articles with their sentiment scores.
    
    Args:
        latest_sentiment: Dictionary with latest sentiment analysis results
    """
    st.header("Bitcoin News Examples")
    
    if not latest_sentiment or 'articles' not in latest_sentiment:
        st.warning("No recent news examples available.")
        return
    
    # Get articles and sort by publication date (most recent first)
    articles = latest_sentiment['articles']
    articles = sorted(articles, key=lambda x: x.get('publishedAt', ''), reverse=True)
    
    # Limit to 5 most recent articles
    articles = articles[:5]
    
    for article in articles:
        # Create expandable container for each article
        with st.expander(f"{article.get('title', 'No Title')}"):
            col1, col2 = st.columns([7, 3])
            
            with col1:
                st.markdown(f"**Source:** {article.get('source', {}).get('name', 'Unknown')}")
                st.markdown(f"**Published:** {article.get('publishedAt', 'Unknown')}")
                st.markdown(f"**Description:** {article.get('description', 'No description available')}")
                
                # Add URL as button
                if article.get('url'):
                    st.markdown(f"[Read Full Article]({article['url']})")
            
            with col2:
                # Display sentiment metrics
                if 'sentiment' in article:
                    sentiment = article['sentiment']
                    polarity = sentiment.get('polarity', 0)
                    subjectivity = sentiment.get('subjectivity', 0)
                    
                    # Determine sentiment color
                    if polarity > 0.05:
                        color = "green"
                        sentiment_label = "Positive"
                    elif polarity < -0.05:
                        color = "red"
                        sentiment_label = "Negative"
                    else:
                        color = "gray"
                        sentiment_label = "Neutral"
                    
                    # Display sentiment score with color
                    st.markdown(f"**Sentiment:** <span style='color:{color}'>{sentiment_label}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Polarity:** {polarity:.3f}")
                    st.markdown(f"**Subjectivity:** {subjectivity:.3f}")