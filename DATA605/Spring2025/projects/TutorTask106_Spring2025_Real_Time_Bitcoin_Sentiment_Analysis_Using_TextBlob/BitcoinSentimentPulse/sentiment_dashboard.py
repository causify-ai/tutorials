"""
Bitcoin Sentiment Analysis Dashboard

This module provides a comprehensive dashboard for visualizing
both hourly and daily Bitcoin sentiment analysis with insights
on how sentiment influences price forecasting.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
import os

# Import sentiment analysis helpers
from sentiment_visualization import (
    load_sentiment_data,
    load_latest_sentiment_info,
    plot_sentiment_trend,
    plot_sentiment_distribution,
    plot_sentiment_by_source,
    sentiment_price_correlation
)

def display_sentiment_dashboard(bitcoin_price_df=None):
    """
    Display a comprehensive sentiment analysis dashboard with hourly and daily insights.
    
    Args:
        bitcoin_price_df: Optional DataFrame with Bitcoin price data for correlation
    """
    st.title("Bitcoin Sentiment Analysis")
    
    # Create dashboard with separate tabs for different types of analysis
    tabs = st.tabs([
        "Sentiment Overview", 
        "Hourly Analysis", 
        "Daily Analysis", 
        "Sentiment-Price Relationship", 
        "News Examples"
    ])
    
    # Overview tab - combined insights
    with tabs[0]:
        st.header("Bitcoin Market Sentiment Overview")
        
        # Load latest sentiment summary from sentiment analysis scheduler
        latest_sentiment = load_latest_sentiment_info()
        
        if latest_sentiment and not isinstance(latest_sentiment, str):
            # Show overall sentiment score
            if 'avg_polarity' in latest_sentiment:
                # Determine sentiment classification
                sentiment_score = latest_sentiment.get('avg_polarity', 0)
                if sentiment_score > 0.05:
                    sentiment_class = "Positive 📈"
                    color = "green"
                elif sentiment_score < -0.05:
                    sentiment_class = "Negative 📉"
                    color = "red"
                else:
                    sentiment_class = "Neutral ↔️"
                    color = "gray"
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(
                        "Current Bitcoin Sentiment",
                        sentiment_class,
                        delta=None
                    )
                
                with col2:
                    st.metric(
                        "Sentiment Score",
                        f"{sentiment_score:.3f}",
                        delta=None
                    )
                
                with col3:
                    positive_articles = latest_sentiment.get('positive_count', 0)
                    negative_articles = latest_sentiment.get('negative_count', 0)
                    neutral_articles = latest_sentiment.get('neutral_count', 0)
                    total_articles = positive_articles + negative_articles + neutral_articles
                    
                    if total_articles > 0:
                        positive_pct = (positive_articles / total_articles) * 100
                    else:
                        positive_pct = 0
                        
                    st.metric(
                        "Positive Articles",
                        f"{positive_articles}/{total_articles}",
                        f"{positive_pct:.1f}%"
                    )
            
            # Daily sentiment trend chart
            st.subheader("Recent Sentiment Trend")
            daily_df = load_sentiment_data('daily', days=7)
            if not daily_df.empty:
                daily_trend = plot_sentiment_trend(daily_df, bitcoin_price_df)
                if daily_trend:
                    st.plotly_chart(daily_trend, use_container_width=True, key="overview_daily_trend")
                    
                # Display sentiment distribution
                st.subheader("Sentiment Distribution")
                sentiment_dist = plot_sentiment_distribution(daily_df)
                if sentiment_dist:
                    st.plotly_chart(sentiment_dist, use_container_width=True, key="overview_sentiment_dist")
            else:
                st.info("No recent sentiment data available. Data will appear once the sentiment analysis system has collected enough articles.")

            # Display sentiment by source
            if 'sources' in latest_sentiment and latest_sentiment['sources']:
                st.subheader("Sentiment by News Source")
                source_chart = plot_sentiment_by_source(latest_sentiment)
                if source_chart:
                    st.plotly_chart(source_chart, use_container_width=True, key="overview_source_chart")
        else:
            st.info("Sentiment data is currently being collected. Please check back in a few minutes.")
            
        # Information about sentiment analysis
        with st.expander("About Bitcoin Sentiment Analysis"):
            st.markdown("""
            This dashboard analyzes sentiment in Bitcoin-related news articles to understand market sentiment.
            
            **How it works:**
            1. News articles about Bitcoin are collected from various sources
            2. TextBlob is used to analyze the sentiment (positive/negative) of each article
            3. Sentiment scores are aggregated and visualized
            4. These insights can help inform trading and investment decisions
            
            **Sentiment Score:** Ranges from -1 (very negative) to +1 (very positive)
            """)
    
    # Hourly sentiment analysis tab
    with tabs[1]:
        st.header("Hourly Bitcoin Sentiment Analysis")
        
        # Load hourly sentiment data
        hourly_df = load_sentiment_data('hourly', days=2)
        
        if not hourly_df.empty:
            # Show metrics
            total_records = len(hourly_df)
            avg_sentiment = hourly_df['avg_polarity'].mean()
            last_sentiment = hourly_df['avg_polarity'].iloc[-1] if total_records > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Recent Hours Analyzed",
                    f"{total_records}",
                    delta=None
                )
            
            with col2:
                st.metric(
                    "Average Hourly Sentiment",
                    f"{avg_sentiment:.3f}",
                    delta=None
                )
            
            with col3:
                delta = last_sentiment - avg_sentiment if total_records > 1 else None
                st.metric(
                    "Latest Hour Sentiment",
                    f"{last_sentiment:.3f}",
                    f"{delta:.3f}" if delta is not None else None
                )
            
            # Hourly sentiment trend plot
            st.subheader("Hourly Sentiment Trend")
            hourly_trend = plot_sentiment_trend(hourly_df)
            if hourly_trend:
                st.plotly_chart(hourly_trend, use_container_width=True, key="hourly_sentiment_trend")
        else:
            st.info("Hourly sentiment data is being collected. Please check back soon.")
    
    # Daily sentiment analysis tab
    with tabs[2]:
        st.header("Daily Bitcoin Sentiment Analysis")
        
        # Load daily sentiment data
        daily_df = load_sentiment_data('daily', days=7)
        
        if not daily_df.empty:
            # Show metrics
            total_days = len(daily_df)
            avg_daily_sentiment = daily_df['avg_polarity'].mean()
            last_daily_sentiment = daily_df['avg_polarity'].iloc[-1] if total_days > 0 else 0
            positive_days = sum(daily_df['avg_polarity'] > 0.05)
            positive_pct = (positive_days / total_days) * 100 if total_days > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Days Analyzed",
                    f"{total_days}",
                    delta=None
                )
            
            with col2:
                st.metric(
                    "Average Daily Sentiment",
                    f"{avg_daily_sentiment:.3f}",
                    delta=None
                )
            
            with col3:
                st.metric(
                    "Positive Days",
                    f"{positive_days}/{total_days}",
                    f"{positive_pct:.1f}%"
                )
            
            # Daily sentiment trend chart
            st.subheader("Daily Sentiment Trend")
            daily_trend = plot_sentiment_trend(daily_df, bitcoin_price_df)
            if daily_trend:
                st.plotly_chart(daily_trend, use_container_width=True, key="daily_sentiment_trend")
            
            # Correlation with price (if price data available)
            if bitcoin_price_df is not None and not bitcoin_price_df.empty:
                st.subheader("Sentiment-Price Correlation")
                correlation, corr_fig = sentiment_price_correlation(daily_df, bitcoin_price_df)
                
                if correlation is not None and corr_fig is not None:
                    # Display correlation strength description
                    if abs(correlation) < 0.2:
                        strength = "very weak"
                    elif abs(correlation) < 0.4:
                        strength = "weak"
                    elif abs(correlation) < 0.6:
                        strength = "moderate"
                    elif abs(correlation) < 0.8:
                        strength = "strong"
                    else:
                        strength = "very strong"
                        
                    direction = "positive" if correlation > 0 else "negative"
                    
                    st.write(f"There is a {strength} {direction} correlation ({correlation:.3f}) between Bitcoin sentiment and subsequent price movement.")
                    
                    if correlation > 0.3:
                        st.success("Positive sentiment tends to precede price increases.")
                    elif correlation < -0.3:
                        st.warning("Negative sentiment tends to precede price decreases.")
                    else:
                        st.info("There is no strong relationship between sentiment and price movement in the current data.")
                    
                    st.plotly_chart(corr_fig, use_container_width=True, key="sentiment_price_correlation")
                else:
                    st.info("Not enough overlapping data to calculate sentiment-price correlation.")
        else:
            st.info("Daily sentiment data is being collected. Please check back soon.")
    
    # Sentiment-price relationship tab
    with tabs[3]:
        # How sentiment analysis improves forecasting
        st.subheader("Sentiment Analysis in Bitcoin Price Forecasting")
        
        # Create visualization of sentiment contribution to model
        st.write("""
        Sentiment analysis plays an important role in Bitcoin price forecasting by capturing market psychology:
        
        1. **Leading Indicator**: News sentiment often precedes price movements
        2. **Market Psychology**: Captures fear and greed cycles in crypto markets
        3. **Complementary Signal**: Provides different information than technical indicators
        4. **Volatility Prediction**: Helps anticipate periods of high volatility
        """)
        
        # Show example of how sentiment is used in forecasting
        st.subheader("How Sentiment Is Used In Forecasting")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Sentiment Features Used:**
            - Daily average sentiment
            - Sentiment volatility
            - Extreme sentiment signals
            - Sentiment trend (improving/deteriorating)
            - Sentiment divergence from price
            """)
            
        with col2:
            st.markdown("""
            **Benefits to Forecast Accuracy:**
            - Earlier detection of trend changes
            - Improved model performance during news-driven events
            - Better handling of non-technical market shifts
            - Reduced false signals during sentiment-driven rallies/selloffs
            """)
            
        # Sentiment-based trading strategies section
        st.subheader("Sentiment-Based Trading Strategies")
        st.write("""
        The sentiment analysis can be used to develop trading strategies:
        
        1. **Contrarian Approach**: Consider buying when sentiment is extremely negative
        2. **Trend Confirmation**: Use positive sentiment to confirm bullish technical signals
        3. **Risk Management**: Reduce position sizes during extremely negative sentiment
        4. **Volatility Anticipation**: Prepare for increased volatility when sentiment shifts rapidly
        """)
    
    # News examples tab
    with tabs[4]:
        st.header("Recent Bitcoin News with Sentiment Analysis")
        
        # Load latest sentiment info with articles
        latest_sentiment = load_latest_sentiment_info()
        articles = []
        
        if latest_sentiment and 'articles' in latest_sentiment:
            articles = latest_sentiment['articles']
            
            # Show top 5 articles with sentiment
            st.write(f"Displaying {min(len(articles), 5)} recent Bitcoin news articles with sentiment analysis:")
            
            for i, article in enumerate(articles[:5]):
                # Format sentiment display
                if 'sentiment' in article:
                    # Handle different sentiment data formats
                    try:
                        if isinstance(article['sentiment'], dict):
                            # Dictionary format with polarity and subjectivity keys
                            polarity = article['sentiment'].get('polarity', 0)
                            subjectivity = article['sentiment'].get('subjectivity', 0)
                        elif isinstance(article['sentiment'], (int, float)):
                            # Direct numeric value
                            polarity = article['sentiment']
                            subjectivity = 0.5  # Default subjectivity if not available
                        elif isinstance(article['sentiment'], str):
                            # Try to convert from string
                            try:
                                polarity = float(article['sentiment'])
                                subjectivity = 0.5
                            except ValueError:
                                polarity = 0
                                subjectivity = 0
                        else:
                            polarity = 0
                            subjectivity = 0
                        
                        # Determine sentiment classification and color
                        if polarity > 0.05:
                            sentiment_class = "Positive"
                            color = "green" 
                        elif polarity < -0.05:
                            sentiment_class = "Negative"
                            color = "red"
                        else:
                            sentiment_class = "Neutral"
                            color = "gray"
                    except Exception as e:
                        st.warning(f"Error processing sentiment data: {str(e)}")
                        polarity = 0
                        subjectivity = 0
                        sentiment_class = "Unknown"
                        color = "gray"
                else:
                    sentiment_class = "Unknown"
                    polarity = 0
                    subjectivity = 0
                    color = "gray"
                
                # Create expandable card for article
                article_title = "No Title"
                try:
                    if isinstance(article, dict) and 'title' in article:
                        article_title = article['title']
                    elif isinstance(article, str):
                        article_title = f"Article {i+1}"
                except Exception as e:
                    article_title = f"Article {i+1} (Error: {str(e)})"
                    
                with st.expander(f"{i+1}. {article_title}"):
                    col1, col2 = st.columns([7, 3])
                    
                    with col1:
                        # Handle different article data formats safely
                        if isinstance(article, dict):
                            # Source information
                            source_name = "Unknown"
                            if 'source' in article:
                                if isinstance(article['source'], dict) and 'name' in article['source']:
                                    source_name = article['source']['name']
                                elif isinstance(article['source'], str):
                                    source_name = article['source']
                            
                            # Other article fields
                            published_date = article.get('publishedAt', 'Unknown')
                            description = article.get('description', 'No description available')
                            url = article.get('url', '')
                            
                            st.markdown(f"**Source:** {source_name}")
                            st.markdown(f"**Published:** {published_date}")
                            st.markdown(f"**Description:** {description}")
                            
                            # Add link to full article
                            if url:
                                st.markdown(f"[Read Full Article]({url})")
                        else:
                            st.markdown("Article details not available in the expected format.")
                    
                    try:
                        with col2:
                            # Display sentiment metrics with color
                            st.markdown(f"**Sentiment:** <span style='color:{color}'>{sentiment_class}</span>", unsafe_allow_html=True)
                            st.markdown(f"**Polarity:** {polarity:.3f}")
                            st.markdown(f"**Subjectivity:** {subjectivity:.3f}")
                    except Exception as e:
                        st.error(f"Error displaying sentiment metrics: {str(e)}")
            
            # Display overall sentiment stats
            if 'avg_polarity' in latest_sentiment:
                avg_polarity = latest_sentiment['avg_polarity']
                st.markdown(f"**Overall Sentiment Score:** {avg_polarity:.3f}")
        else:
            st.info("Currently collecting Bitcoin news articles. Please check back soon for news examples with sentiment analysis.")

def display_scheduled_analysis_section():
    """Display a section about the scheduled sentiment analysis system."""
    st.subheader("Scheduled Sentiment Analysis System")
    
    st.write("""
    The Bitcoin sentiment analysis system runs automatically on a schedule:
    
    - **Hourly Analysis**: Quick sentiment check from recent Bitcoin news
    - **Daily Analysis**: Comprehensive sentiment analysis with larger data sample
    
    This ensures you always have the latest sentiment data for your forecasting models.
    """)
    
    st.info("The sentiment scheduler is running in the background continuously collecting and analyzing Bitcoin news.")