import streamlit as st
import datetime
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import numpy as np
import os
import threading
import pytz

# Import custom modules
from src.data_collector import DataCollector
from src.model import BitcoinForecastModel
from src.model_factory import ModelFactory, ModelType
from src.technical_indicators import calculate_indicators
from src.visualizer import (
    plot_price_with_forecast,
    plot_technical_indicators,
    plot_forecast_components,
    plot_model_metrics,
    plot_uncertainty,
)
from src.utils import format_large_number, get_color_from_value
from src.sentiment_integration import SentimentIntegrator

# Import optimized sentiment analysis helpers
from sentiment_analysis_helper import update_sentiment_display, get_top_bitcoin_sentiment
from bitcoin_sentiment import BitcoinSentimentAnalyzer
from sentiment_scheduler import start_sentiment_scheduling, get_sentiment_for_forecasting, get_latest_sentiment
from sentiment_visualization import load_sentiment_data, plot_sentiment_trend, sentiment_price_correlation, display_news_examples

# Page configuration
st.set_page_config(
    page_title="Bitcoin Price Forecasting System",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state variables
if "data_loaded" not in st.session_state:
    st.session_state.data_loaded = False
if "model_trained" not in st.session_state:
    st.session_state.model_trained = False
if "forecast_data" not in st.session_state:
    st.session_state.forecast_data = None
if "error_metrics" not in st.session_state:
    st.session_state.error_metrics = None
if "components" not in st.session_state:
    st.session_state.components = None
if "sentiment_data" not in st.session_state:
    st.session_state.sentiment_data = None
if "last_update_time" not in st.session_state:
    st.session_state.last_update_time = None
if "update_frequency" not in st.session_state:
    st.session_state.update_frequency = 60  # Default update every 60 seconds

def update_data():
    """Update real-time Bitcoin price and sentiment data"""
    try:
        # Update price data
        if st.session_state.data_loaded:
            dc = DataCollector(source='yfinance')  # Using YFinance for real-time updates
            bitcoin_data = dc.get_historical_data(period='7d')  # Get latest week data
            st.session_state.bitcoin_data = bitcoin_data
            
            # Calculate technical indicators
            st.session_state.technical_indicators = calculate_indicators(bitcoin_data)
            
            # Update sentiment data
            sentiment_integrator = SentimentIntegrator()
            
            # Get sentiment data based on saved parameters or defaults
            use_sentiment = st.session_state.get('use_sentiment', True)
            sentiment_days = st.session_state.get('sentiment_days', 28)  # Default to free tier

            # Update sentiment display data
            sentiment_summary = sentiment_integrator.get_sentiment_summary()
            st.session_state.sentiment_data = sentiment_summary
            
            # Update last update time
            st.session_state.last_update_time = datetime.datetime.now()
            
            # Auto-update forecast if model was trained
            if st.session_state.model_trained and hasattr(st.session_state, 'model_params'):
                # Get sentiment features for forecasting if enabled
                sentiment_data = None
                if use_sentiment:
                    sentiment_df = sentiment_integrator.get_sentiment_data(days=sentiment_days)
                    if not sentiment_df.empty:
                        sentiment_data = sentiment_integrator.create_sentiment_features(bitcoin_data)
                        st.session_state.sentiment_features = sentiment_data
                        # Log successful sentiment integration
                        print(f"Integrated {len(sentiment_df)} sentiment records into forecast")
                    else:
                        print("No sentiment data available for forecast integration")
                
                # Re-train model with new data
                model = BitcoinForecastModel(**st.session_state.model_params)
                forecast_results = model.fit_and_forecast(
                    st.session_state.bitcoin_data,
                    sentiment_data=sentiment_data if use_sentiment else None
                )
                
                # Store updated results
                st.session_state.forecast_data = forecast_results['forecast']
                st.session_state.components = forecast_results['components']
                st.session_state.error_metrics = forecast_results['metrics']
                st.session_state.used_sentiment = forecast_results.get('used_sentiment', False)
    
    except Exception as e:
        st.error(f"Error updating data: {str(e)}")

def main():
    # Custom CSS for some minor adjustments
    st.markdown("""
        <style>
        .big-font {
            font-size:30px !important;
            font-weight: bold;
        }
        .medium-font {
            font-size:20px !important;
        }
        .stProgress .st-bo {
            background-color: #F63366;
        }
        </style>
        """, unsafe_allow_html=True)
    
    # Start sentiment analysis scheduling in background
    start_sentiment_scheduling()

    # Sidebar configuration
    with st.sidebar:
        st.image("https://pixabay.com/get/g9c78f9036baf0d159e2e6abf9b5348c91d0913bcc0f332ba641193bcfee0febdd76d066e1407d37400b114b004df716dd4134ad5cd439efd30e676758fb594bf_1280.jpg", width=250)
        st.title("Bitcoin Price Forecast")
        st.subheader("Configuration")
        
        # Data parameters
        st.subheader("Data Parameters")
        data_source = st.selectbox(
            "Data Source",
            options=["CoinGecko", "YFinance"],
            index=0
        )
        
        time_period = st.selectbox(
            "Historical Data Period",
            options=["7d", "30d", "90d", "180d", "365d", "max"],
            index=2
        )
        
        # Model parameters
        st.subheader("Model Parameters")
        
        # Add model limitations notice
        # st.info("⚠️ Note: This version uses ARIMA models for all forecasting. Advanced models (LSTM/Transformer) are simulated using ARIMA with appropriate configurations.")
        
        # Sentiment analysis configuration
        st.subheader("Sentiment Analysis")
        use_sentiment = st.checkbox("Use Sentiment Analysis in Forecast", value=True)
        
        api_tier = st.radio(
            "NewsAPI Tier",
            ["Free (limited to last 28 days)", "Paid (full historical data)"],
            index=0,
            help="Free tier restricts news articles to the most recent 28 days"
        )
        sentiment_days = 28 if api_tier.startswith("Free") else 90
        
        # Model type selection
        model_type = st.selectbox(
            "Model Type",
            options=["LSTM (Neural Network)", "ARIMA (Statistical)"], # "Transformer (Attention-based)", "Ensemble (Combined)"],
            index=0,
            help="Select the type of forecasting model to use"
        )
        
        # Convert user-friendly names to internal model types
        model_type_map = {
            "ARIMA (Statistical)": "arima",
            "LSTM (Neural Network)": "lstm",
            "Transformer (Attention-based)": "transformer",
            "Ensemble (Combined)": "ensemble"
        }
        selected_model_type = model_type_map[model_type]
        
        # Common parameters for all models
        forecast_horizon = st.slider(
            "Forecast Horizon (Days)",
            min_value=1,
            max_value=30,
            value=7
        )
        
        confidence_level = st.slider(
            "Confidence Level (%)",
            min_value=50,
            max_value=99,
            value=90,
            step=1
        )
        
        # Model-specific parameters
        if selected_model_type == "lstm":
            st.subheader("LSTM Parameters")
            lookback_window = st.slider("Lookback Window (Days)", min_value=7, max_value=60, value=30, 
                                       help="Number of past days to use for prediction")
            lstm_units = st.slider("LSTM Units", min_value=16, max_value=128, value=64, step=16,
                                  help="Number of LSTM units (neurons) in each layer")
            dropout_rate = st.slider("Dropout Rate", min_value=0.0, max_value=0.5, value=0.2, step=0.1,
                                    help="Dropout rate for regularization")
            learning_rate = st.slider("Learning Rate", min_value=0.0001, max_value=0.01, value=0.001, step=0.0001,
                                     help="Learning rate for model training")
            batch_size = st.slider("Batch Size", min_value=8, max_value=64, value=32, step=8,
                                  help="Batch size for training")
            epochs = st.slider("Epochs", min_value=10, max_value=200, value=100, step=10,
                              help="Number of training epochs")
            
            # Store LSTM-specific parameters
            st.session_state.model_params = {
                'forecast_horizon': forecast_horizon,
                'lookback_window': lookback_window,
                'hidden_units': lstm_units,
                'dropout_rate': dropout_rate,
                'learning_rate': learning_rate,
                'batch_size': batch_size,
                'epochs': epochs,
                'include_sentiment': use_sentiment
            }
            
        elif selected_model_type == "transformer":
            st.subheader("Transformer Parameters")
            lookback_window = st.slider("Lookback Window (Days)", min_value=7, max_value=60, value=30,
                                       help="Number of past days to use for prediction")
            embed_dim = st.slider("Embedding Dimension", min_value=16, max_value=128, value=32, step=16,
                                 help="Dimension of the embedding layer")
            num_heads = st.slider("Number of Attention Heads", min_value=1, max_value=8, value=2, step=1,
                                 help="Number of attention heads in transformer")
            ff_dim = st.slider("Feed-forward Dimension", min_value=16, max_value=128, value=32, step=16,
                              help="Dimension of the feed-forward network")
            num_blocks = st.slider("Number of Transformer Blocks", min_value=1, max_value=6, value=2, step=1,
                                  help="Number of transformer blocks")
            dropout_rate = st.slider("Dropout Rate", min_value=0.0, max_value=0.5, value=0.1, step=0.1,
                                    help="Dropout rate for regularization")
            learning_rate = st.slider("Learning Rate", min_value=0.0001, max_value=0.01, value=0.001, step=0.0001,
                                     help="Learning rate for model training")
            batch_size = st.slider("Batch Size", min_value=8, max_value=64, value=32, step=8,
                                  help="Batch size for training")
            epochs = st.slider("Epochs", min_value=10, max_value=200, value=100, step=10,
                              help="Number of training epochs")
            
            # Store Transformer-specific parameters
            st.session_state.model_params = {
                'forecast_horizon': forecast_horizon,
                'lookback_window': lookback_window,
                'embed_dim': embed_dim,
                'num_heads': num_heads,
                'ff_dim': ff_dim,
                'num_transformer_blocks': num_blocks,
                'dropout_rate': dropout_rate,
                'learning_rate': learning_rate,
                'batch_size': batch_size,
                'epochs': epochs,
                'include_sentiment': use_sentiment
            }
            
        elif selected_model_type == "arima":
            st.subheader("ARIMA Parameters")
            use_mcmc = st.checkbox("Use Complex Model", value=False,
                                 help="Use more complex ARIMA parameters")
            include_trend = st.checkbox("Include Trend", value=True,
                                      help="Include trend component in the model")
            include_seasonality = st.checkbox("Include Seasonality", value=True,
                                            help="Include seasonality in the model")
            include_autoregressive = st.checkbox("Include Autoregressive", value=True,
                                               help="Include autoregressive component")
            
            # Store ARIMA-specific parameters
            st.session_state.model_params = {
                'forecast_horizon': forecast_horizon,
                'use_mcmc': use_mcmc,
                'include_trend': include_trend,
                'include_seasonality': include_seasonality,
                'include_autoregressive': include_autoregressive,
                'confidence_level': confidence_level / 100.0
            }
            
        elif selected_model_type == "ensemble":
            st.subheader("Ensemble Parameters")
            # Store common parameters for ensemble
            st.session_state.model_params = {
                'forecast_horizon': forecast_horizon,
                'confidence_level': confidence_level / 100.0,
                'include_sentiment': use_sentiment
            }
        
        # Technical indicators
        st.subheader("Technical Indicators")
        show_ma = st.checkbox("Moving Averages", value=True)
        show_rsi = st.checkbox("RSI", value=True)
        show_macd = st.checkbox("MACD", value=True)
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            load_data_btn = st.button("Load Data", use_container_width=True)
        with col2:
            train_model_btn = st.button("Train Model", use_container_width=True)
        
        # Credits
        st.markdown("---")
        st.caption("Developed using TensorFlow Probability and Streamlit")

    # Main area - Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("Bitcoin Price Forecasting System")
        st.subheader("Advanced Time Series Analysis with Uncertainty Quantification")
    with col2:
        # Current price section will be updated when data is loaded
        st.markdown('<p class="medium-font">Current BTC Price</p>', unsafe_allow_html=True)
        if st.session_state.data_loaded:
            latest_price = float(st.session_state.bitcoin_data.iloc[-1]['price'])
            previous_price = float(st.session_state.bitcoin_data.iloc[-2]['price'])
            price_change = latest_price - previous_price
            price_change_pct = (price_change / previous_price) * 100
            color = "green" if price_change >= 0 else "red"
            arrow = "↑" if price_change >= 0 else "↓"
            st.markdown(f'<p class="big-font" style="color:{color};">${format_large_number(latest_price)} {arrow}</p>', unsafe_allow_html=True)
            st.markdown(f'<p style="color:{color};">{arrow} ${abs(price_change):.2f} ({abs(price_change_pct):.2f}%)</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="big-font">$--,---</p>', unsafe_allow_html=True)
            st.markdown('<p>-- (--)</p>', unsafe_allow_html=True)
    
    # Create main application tabs
    main_tabs = st.tabs(["Price Forecasting", "Sentiment Analysis", "Technical Analysis"])
    
    with main_tabs[0]:
        # Price Forecasting Tab Content
        st.header("Bitcoin Price Forecasting")
        
        # Placeholder for forecasting content
        if not st.session_state.data_loaded:
            st.info("Please load the data first by clicking the 'Load Data' button in the sidebar.")
        else:
            if not st.session_state.model_trained:
                st.info("Data loaded. Please train the model using the 'Train Model' button in the sidebar.")
            else:
                # Show current trained model details
                model_params = st.session_state.model_params
                st.subheader(f"Forecast using {model_type}")
                
                # Display real-time price updates
                current_price = st.session_state.bitcoin_data.iloc[-1]['price']
                forecast_results = st.session_state.forecast_data
                
                # Show forecast visualizations
                st.subheader("Bitcoin Price Forecast")
                
                # Display the forecast plot with uncertainty
                fig = plot_price_with_forecast(
                    st.session_state.bitcoin_data,
                    forecast_results,  # Pass the entire results dictionary
                    confidence_level=confidence_level
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Show model components if available (ARIMA only)
                if st.session_state.components is not None and selected_model_type == "arima":
                    with st.expander("Forecast Components Analysis", expanded=False):
                        components_fig = plot_forecast_components(st.session_state.components)
                        st.plotly_chart(components_fig, use_container_width=True)
                
                # Show model metrics
                col1, col2 = st.columns(2)
                with col1:
                    with st.expander("Model Accuracy Metrics", expanded=False):
                        if st.session_state.error_metrics is not None:
                            metrics_fig = plot_model_metrics(st.session_state.error_metrics)
                            st.plotly_chart(metrics_fig, use_container_width=True)
                
                with col2:
                    with st.expander("Price Uncertainty Analysis", expanded=False):
                        uncertainty_fig = plot_uncertainty(forecast_results, confidence_level=confidence_level)  # Pass the entire results dictionary
                        st.plotly_chart(uncertainty_fig, use_container_width=True)
                
                # Add price targets
                with st.expander("Price Target Alerts", expanded=False):
                    st.subheader("Set Price Targets")
                    
                    # Get current price value (safely handles both Series and scalar values)
                    if hasattr(current_price, 'iloc'):
                        current_price_value = float(current_price.iloc[0])
                    else:
                        current_price_value = float(current_price)
                        
                    price_target = st.number_input(
                        "Price Target ($)",
                        min_value=1000.0,
                        max_value=200000.0,  # Increased max value to accommodate higher Bitcoin prices
                        value=min(current_price_value * 1.1, 190000.0),  # Default to 10% above current, but capped
                        step=100.0
                    )
                    
                    # Calculate probability of reaching target
                    if price_target > current_price_value:
                        # Calculate probability of price exceeding target within forecast horizon
                        target_probs = []
                        forecast_data = forecast_results  # Use the forecast data directly
                        
                        if isinstance(forecast_data, pd.DataFrame):
                            # DataFrame format (LSTM model)
                            for i in range(len(forecast_data)):
                                if forecast_data['Upper_CI'].iloc[i] >= price_target:
                                    mean = forecast_data['Forecast'].iloc[i]
                                    std = (forecast_data['Upper_CI'].iloc[i] - mean) / 1.96  # Assuming 95% CI
                                    
                                    # Calculate probability using normal CDF
                                    from scipy.stats import norm
                                    prob = 1 - norm.cdf(price_target, loc=mean, scale=std)
                                    target_probs.append(prob)
                                else:
                                    target_probs.append(0)
                        else:
                            # Dictionary format (ARIMA model)
                            for i in range(len(forecast_data['upper'])):
                                if forecast_data['upper'][i] >= price_target:
                                    mean = forecast_data['mean'][i]
                                    std = forecast_data['stddev'][i]
                                    
                                    # Calculate probability using normal CDF
                                    from scipy.stats import norm
                                    prob = 1 - norm.cdf(price_target, loc=mean, scale=std)
                                    target_probs.append(prob)
                                else:
                                    target_probs.append(0)
                        
                        max_prob = max(target_probs) * 100
                        day_max_prob = target_probs.index(max(target_probs)) + 1
                        
                        # Display the probability
                        st.subheader(f"Target: ${price_target:,.2f}")
                        st.metric("Max. Probability of Reaching Target", f"{max_prob:.1f}%", f"Day {day_max_prob}")
                        
                        # Create a gauge chart for the probability
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=max_prob,
                            domain={'x': [0, 1], 'y': [0, 1]},
                            gauge={
                                'axis': {'range': [0, 100]},
                                'bar': {'color': "darkblue"},
                                'steps': [
                                    {'range': [0, 30], 'color': "red"},
                                    {'range': [30, 70], 'color': "yellow"},
                                    {'range': [70, 100], 'color': "green"}
                                ]
                            },
                            title={'text': "Probability of Reaching Target"}
                        ))
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Price target should be higher than the current price.")
    
    with main_tabs[1]:
        # Sentiment Analysis Dashboard
        st.header("Bitcoin Sentiment Analysis")
        
        # Add session state variable to track if using sentiment in forecasting
        if "used_sentiment" not in st.session_state:
            st.session_state.used_sentiment = False
        
        if st.session_state.data_loaded:
            # Import our sentiment dashboard components
            from sentiment_dashboard import display_sentiment_dashboard, display_scheduled_analysis_section
            
            # Use our comprehensive sentiment dashboard
            display_sentiment_dashboard(bitcoin_price_df=st.session_state.bitcoin_data)
            
            # Show information about the scheduled analysis system
            st.markdown("---")
            display_scheduled_analysis_section()
            
            # Show how sentiment is used in forecasting
            if st.session_state.forecast_data is not None and st.session_state.used_sentiment:
                st.success("Sentiment analysis is actively influencing your current Bitcoin price forecast.")
            else:
                st.info("Enable sentiment analysis in the model settings to incorporate news sentiment into price predictions.")
        else:
            st.info("Please load data first using the 'Load Data' button in the sidebar.")
    
    with main_tabs[2]:
        # Technical Analysis Tab
        st.header("Technical Indicators Analysis")
        
        if st.session_state.data_loaded:
            tech_indicators = st.session_state.technical_indicators
            
            # Generate and display technical analysis charts
            st.subheader("Price with Technical Indicators")
            
            # Create the technical indicators chart
            fig = plot_technical_indicators(
                st.session_state.bitcoin_data,
                show_rsi='rsi' in tech_indicators,
                show_macd='macd' in tech_indicators
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Add technical indicator explanations
            with st.expander("Technical Indicators Explained"):
                st.markdown("""
                ### Moving Averages
                Moving averages smooth out price data to create a single flowing line, making it easier to identify the direction of the trend.
                - **SMA (Simple Moving Average)**: The simple average of prices over a specific period.
                - **EMA (Exponential Moving Average)**: A type of moving average that gives more weight to recent prices.
                
                ### RSI (Relative Strength Index)
                RSI is a momentum oscillator that measures the speed and change of price movements.
                - **Values from 0-100**: Typically, RSI above 70 is considered overbought, while RSI below 30 is considered oversold.
                
                ### MACD (Moving Average Convergence Divergence)
                MACD is a trend-following momentum indicator that shows the relationship between two moving averages.
                - **MACD Line**: Calculated by subtracting the 26-period EMA from the 12-period EMA.
                - **Signal Line**: 9-period EMA of the MACD Line.
                - **Histogram**: The difference between the MACD Line and the Signal Line.
                """)
        else:
            st.info("Please load data first using the 'Load Data' button in the sidebar.")
    
    # Data loading and model training logic
    if load_data_btn:
        with st.spinner("Loading Bitcoin price data..."):
            try:
                # Use lowercase source name for the collector
                source = data_source.lower()
                if "yfinance" in source:
                    source = "yfinance"
                elif "coingecko" in source:
                    source = "coingecko"
                
                # Create data collector and get data
                dc = DataCollector(source=source)
                bitcoin_data = dc.get_historical_data(period=time_period)
                
                if bitcoin_data.empty:
                    st.error("❌ No data was returned from the data source. Please try a different data source or time period.")
                else:
                    # Store data in session state
                    st.session_state.bitcoin_data = bitcoin_data
                    st.session_state.data_loaded = True
                    
                    # Calculate technical indicators
                    st.session_state.technical_indicators = calculate_indicators(bitcoin_data)
                    
                    st.success(f"✅ Successfully loaded Bitcoin price data for the last {time_period} ({len(bitcoin_data)} records)")
                    
                    # Show a sample of the data
                    with st.expander("View loaded data sample"):
                        st.dataframe(bitcoin_data.head())
                    
                    # Also load sentiment data
                    try:
                        sentiment_analyzer = BitcoinSentimentAnalyzer()
                        sentiment_data = sentiment_analyzer.get_sentiment_dataframe(days=sentiment_days)
                        st.session_state.sentiment_data = sentiment_data
                        st.info("✅ Loaded sentiment data for forecasting")
                    except Exception as e:
                        st.warning(f"⚠️ Sentiment data could not be loaded: {str(e)}")
                    
                    # Set last update time
                    st.session_state.last_update_time = datetime.datetime.now()
            except Exception as e:
                st.error(f"❌ Error loading Bitcoin data: {str(e)}")
                st.info("Please try a different data source or time period.")
    
    if train_model_btn:
        if not st.session_state.data_loaded:
            st.error("❌ Please load data first")
        else:
            with st.spinner("Training forecasting model..."):
                # Create model with appropriate parameters
                model_params = {
                    'forecast_horizon': forecast_horizon
                }
                
                # Add model-specific parameters
                if selected_model_type == "lstm":
                    model_params.update({
                        'lookback_window': lookback_window,
                        'hidden_units': lstm_units,
                        'dropout_rate': dropout_rate,
                        'learning_rate': learning_rate,
                        'batch_size': batch_size,
                        'epochs': epochs,
                        'include_sentiment': use_sentiment
                    })
                elif selected_model_type == "transformer":
                    model_params.update({
                        'lookback_window': lookback_window,
                        'embed_dim': embed_dim,
                        'num_heads': num_heads,
                        'ff_dim': ff_dim,
                        'num_transformer_blocks': num_blocks,
                        'dropout_rate': dropout_rate,
                        'learning_rate': learning_rate,
                        'batch_size': batch_size,
                        'epochs': epochs,
                        'include_sentiment': use_sentiment
                    })
                elif selected_model_type == "ensemble":
                    model_params.update({
                        'model_types': ensemble_models,
                        'weights': ensemble_weights,
                        'include_sentiment': use_sentiment
                    })
                else:  # ARIMA model
                    model_params.update({
                        'confidence_level': confidence_level / 100.0,
                        'use_mcmc': use_mcmc,
                        'include_trend': include_trend,
                        'include_seasonality': include_seasonality,
                        'include_autoregressive': include_autoregressive
                    })
                
                # Store model parameters for future updates
                st.session_state.model_params = model_params
                
                # Create and train model
                try:
                    # Get sentiment data if enabled
                    sentiment_data = None
                    if use_sentiment:
                        try:
                            sentiment_integrator = SentimentIntegrator()
                            sentiment_df = sentiment_integrator.get_sentiment_data(days=sentiment_days)
                            if not sentiment_df.empty:
                                sentiment_data = sentiment_integrator.create_sentiment_features(st.session_state.bitcoin_data)
                                st.session_state.sentiment_features = sentiment_data
                                print(f"Integrated {len(sentiment_df)} sentiment records into forecast")
                            else:
                                print("No sentiment data available for forecast integration")
                        except Exception as e:
                            st.warning(f"⚠️ Could not use sentiment data for forecasting: {str(e)}")
                    
                    # Create model using factory
                    model_factory = ModelFactory()
                    model = model_factory.create_model(selected_model_type, **model_params)
                    
                    # Train the model and get forecast
                    forecast_results = model.fit_and_forecast(
                        st.session_state.bitcoin_data,
                        sentiment_data=sentiment_data if use_sentiment else None
                    )
                    
                    # Store results in session state
                    st.session_state.forecast_data = forecast_results['forecast']  # Store just the forecast data
                    st.session_state.components = forecast_results.get('components', None)
                    st.session_state.error_metrics = forecast_results.get('metrics', None)
                    st.session_state.model_trained = True
                    st.session_state.used_sentiment = forecast_results.get('used_sentiment', False)
                    
                    # Success message
                    st.success(f"✅ Successfully trained {selected_model_type} model for Bitcoin forecasting")
                except Exception as e:
                    st.error(f"❌ Error training model: {str(e)}")

    # Set up automatic data updates
    if st.session_state.data_loaded and st.session_state.model_trained:
        # Only show this expander if data is loaded and model is trained
        with st.expander("Real-time Updates Configuration", expanded=False):
            st.subheader("Auto-update Settings")
            
            update_frequency = st.slider(
                "Update Frequency (seconds)",
                min_value=30,
                max_value=300,
                value=st.session_state.update_frequency,
                step=30
            )
            
            # Store the update frequency in session state
            st.session_state.update_frequency = update_frequency
            
            # Show last update time if available
            if st.session_state.last_update_time:
                last_update = st.session_state.last_update_time
                time_diff = datetime.datetime.now() - last_update
                seconds_ago = int(time_diff.total_seconds())
                st.info(f"Last updated: {last_update.strftime('%H:%M:%S')} ({seconds_ago} seconds ago)")
            
            # Button to manually trigger an update
            if st.button("Update Now"):
                with st.spinner("Updating data and forecast..."):
                    update_data()
                st.success("✅ Data and forecast updated!")
        
        # Set up automatic updates
        time_since_update = 0
        if st.session_state.last_update_time:
            time_diff = datetime.datetime.now() - st.session_state.last_update_time
            time_since_update = int(time_diff.total_seconds())
        
        # Create a small progress indicator at the bottom of the page
        update_frequency = st.session_state.update_frequency
        progress_pct = min(time_since_update / update_frequency, 1.0)
        
        # Display the progress bar and status
        if progress_pct >= 1.0:
            # If it's time to update, do it automatiacly
            update_data()
            # Reset the last update time
            st.session_state.last_update_time = datetime.datetime.now()
        
        # Always show progress bar
        st.progress(progress_pct)
        
        # Create a time-to-next-update indicator
        time_to_update = max(0, update_frequency - time_since_update)
        st.caption(f"Next auto-update in {time_to_update} seconds")

# Run the app
if __name__ == "__main__":
    main()