# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
import datetime
from bitcoinchatbot import CryptoAssistant
from price_predictor import BitcoinPricePredictor
import time
import gc
import os 
gc.collect()
# Page configuration
st.set_page_config(
    page_title="BitcoinChat AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'assistant' not in st.session_state:
    st.session_state.assistant = None
if 'price_predictor' not in st.session_state:
    st.session_state.price_predictor = None
if 'initialized' not in st.session_state:
    st.session_state.initialized = False

if 'tool_result' not in st.session_state:
    st.session_state.tool_result = None
if 'current_query' not in st.session_state:
    st.session_state.current_query = None


@st.cache_data(ttl=3600)  # Cache for an hour
def get_historical_data(assistant):
    if assistant and 'bitcoin' in assistant.crypto_data.historical_data:
        return assistant.crypto_data.historical_data['bitcoin']
    return None

# Apply custom styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #F7931A;
        margin-bottom: 1rem;
    }
    .price-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
        margin: 1rem 0;
    }
    .crypto-price {
        font-size: 2rem;
        font-weight: bold;
        color: #F7931A;
    }
    .crypto-change-positive {
        color: #4CAF50;
        font-weight: bold;
    }
    .crypto-change-negative {
        color: #F44336;
        font-weight: bold;
    }
    .tool-result {
        margin-top: 1rem;
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        border-left: 5px solid #F7931A;
    }
</style>
""", unsafe_allow_html=True)


# Sidebar
with st.sidebar:
    st.image("https://bitcoin.org/img/icons/opengraph.png", width=100)
    st.markdown("## Bitcoin Assistant")
    
    # Initialize on first run
    if not st.session_state.initialized:
        with st.spinner("Initializing Bitcoin Assistant..."):
            # Initialize the assistant and price predictor
            st.session_state.assistant = CryptoAssistant()
            st.session_state.assistant.initialize()
            st.session_state.assistant.start_update_thread()
            
            # Replace this block with the new code
            try:
                st.session_state.price_predictor = BitcoinPricePredictor()
                st.session_state.price_predictor.load_model()
            except Exception as e:
                st.error(f"Error loading prediction model: {e}")
                st.session_state.price_predictor = None
                
            st.session_state.initialized = True

# Add this in the sidebar section
    if st.session_state.price_predictor and st.session_state.price_predictor.model:
        st.sidebar.success("✓ LSTM model loaded successfully")
        if os.path.exists(st.session_state.price_predictor.model_path):
            mod_time = datetime.datetime.fromtimestamp(
                os.path.getmtime(st.session_state.price_predictor.model_path)
            )
            st.sidebar.info(f"Model last updated: {mod_time.strftime('%Y-%m-%d %H:%M')}")
    else:
        st.sidebar.warning("⚠ LSTM model not loaded")

    
    # Tools section
    st.markdown("### Tools")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Market Summary"):
         with st.spinner("Generating market summary..."):
            summary = st.session_state.assistant.get_coins_summary()
            st.session_state.tool_result = {"type": "summary", "content": summary}  # Add this line
            st.session_state.messages.append({"role": "user", "content": "Show market summary"})
            st.session_state.messages.append({"role": "assistant", "content": summary})
    
    with col2:
        if st.button("📈 Sentiment Analysis"):  # Add this line
            with st.spinner("Analyzing market sentiment..."):
                sentiment = st.session_state.assistant.get_sentiment_analysis()
                st.session_state.tool_result = {"type": "sentiment", "content": sentiment}
                st.session_state.messages.append({"role": "user", "content": "What's the market sentiment?"})
                st.session_state.messages.append({"role": "assistant", "content": sentiment})
        
    # Price prediction tool
    st.markdown("### Bitcoin Price Prediction")
    days_ahead = st.slider("Days to predict:", 1, 30, 7)
    
    if st.button("Generate Prediction"):
        with st.spinner("Generating price prediction..."):
            if 'bitcoin' in st.session_state.assistant.crypto_data.historical_data:
                historical_data = st.session_state.assistant.crypto_data.historical_data['bitcoin']
                prediction = st.session_state.price_predictor.predict_future(historical_data, days_ahead)
                
                if "error" not in prediction:
                    # Create chat messages with the prediction results
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": f"Predict Bitcoin price {days_ahead} days ahead"
                    })
                    
                    # Prediction answer with chart data
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": f"Based on my analysis, Bitcoin price is predicted to reach ${prediction['expected_price_after_period']:.2f} in {days_ahead} days (a {prediction['predicted_change_percent']:.2f}% change from current price of ${prediction['current_price']:.2f}).",
                        "prediction_data": prediction
                    })
                else:
                    st.error(f"Prediction error: {prediction['error']}")
    

    # Sample Questions Section
    st.subheader("Sample Questions")
    st.markdown("Click on any question to ask it:")

    # Create two columns for better layout of sample questions
    col1, col2 = st.columns(2)

    sample_questions = [
        "What is the current Bitcoin price?",
        " what's the price change for march 15 2015?",
        "How has Bitcoin performed over the last 7 days?",
        "What was the price of Bitcoin on May 10, 2025?",
        "What's the market sentiment right now?",
        "What are the technical indicators for Bitcoin?",
        "Predict Bitcoin price 14 days ahead",
        "What was Bitcoin's highest price in the last month?",
        "Compare Bitcoin's volatility to its historical average"
    ]

    # Add sample questions as clickable elements
    for i, question in enumerate(sample_questions):
        col = col1 if i % 2 == 0 else col2
        q_button = col.button(f"{question}", key=f"sample_q_{i}")
        if q_button:
            # When clicked, set as current query
            st.session_state.current_query = question
   
    # About section - Enhanced with clearer description
    st.markdown("### About")
    st.markdown("""
    **BitcoinChat AI** delivers real-time cryptocurrency insights through:

    • **RAG-Based LLM**: Provides accurate information from multiple trusted sources
    • **LSTM Neural Network**: Powers price prediction functionality
    • **Real-Time Data**: Integrates current market conditions and historical trends
    • **Technical Analysis**: Evaluates key indicators like RSI, MACD, and Bollinger Bands

    Built with Streamlit, Python, TensorFlow, and Ollama running Mistral.
    """)


# Main content area
st.markdown("<h1 class='main-header'>BitcoinChat AI Assistant</h1>", unsafe_allow_html=True)

# Current Bitcoin price card
if st.session_state.initialized and st.session_state.assistant.crypto_data.price_data:
    try:
        btc_data = st.session_state.assistant.crypto_data.price_data.get("bitcoin", {})
        
        st.markdown("<div class='price-card'>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image("https://bitcoin.org/img/icons/opengraph.png", width=80)
            
        with col2:
            btc_price = btc_data.get('usd', 'N/A')
            btc_change = btc_data.get('usd_24h_change', 0)
            change_class = "crypto-change-positive" if btc_change >= 0 else "crypto-change-negative"
            change_sign = "+" if btc_change >= 0 else ""
            
            st.markdown(f"""
            <h3>Bitcoin (BTC)</h3>
            <div class='crypto-price'>${btc_price:,.2f}</div>
            <div class='{change_class}'>{change_sign}{btc_change:.2f}% (24h)</div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not load current price data: {e}")
# Main content area
 

# Display tool results if available
if st.session_state.tool_result:
    st.markdown("<div class='tool-result'>", unsafe_allow_html=True)
    
    if st.session_state.tool_result["type"] == "summary":
        st.subheader("📊 Market Summary")
        st.write(st.session_state.tool_result["content"])
    
    elif st.session_state.tool_result["type"] == "sentiment":
        st.subheader("📈 Market Sentiment Analysis")
        st.write(st.session_state.tool_result["content"])
    
    elif st.session_state.tool_result["type"] == "prediction":
        pred_data = st.session_state.tool_result["content"]
        st.subheader(f"Bitcoin Price Prediction - Next {pred_data['days_ahead']} Days")
        
        # Create Plotly figure for prediction visualization
        fig = go.Figure()
        
        # Add historical price line (last 30 days)
        if 'bitcoin' in st.session_state.assistant.crypto_data.historical_data:
            hist_data = st.session_state.assistant.crypto_data.historical_data['bitcoin'].iloc[-30:]
            fig.add_trace(go.Scatter(
                x=hist_data['date'],
                y=hist_data['price'],
                mode='lines',
                name='Historical Price',
                line=dict(color='#1E88E5')
            ))
        
        # Add prediction line
        pred_dates = [datetime.datetime.strptime(date, '%Y-%m-%d') for date in pred_data['predicted_dates']]
        fig.add_trace(go.Scatter(
            x=pred_dates,
            y=pred_data['predicted_prices'],
            mode='lines',
            name='Price Prediction',
            line=dict(color='#F7931A', dash='dash')
        ))
        
        # Update layout
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            template="plotly_white",
            height=400
        )
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
        
        # Display prediction metrics
        col1, col2, col3 = st.columns(3)
        col1.metric(
            "Current Price", 
            f"${pred_data['current_price']:,.2f}"
        )
        col2.metric(
            f"Predicted ({len(pred_dates)} days)", 
            f"${pred_data['expected_price_after_period']:,.2f}"
        )
        col3.metric(
            "Expected Change", 
            f"{pred_data['predicted_change_percent']:.2f}%",
            delta_color="normal"
        )
    
    st.markdown("</div>", unsafe_allow_html=True)

# Current Bitcoin price card
if st.session_state.initialized and st.session_state.assistant.crypto_data.price_data:
    try:
        btc_data = st.session_state.assistant.crypto_data.price_data.get("bitcoin", {})
        
        st.markdown("<div class='price-card'>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.image("https://bitcoin.org/img/icons/opengraph.png", width=80)
            
        with col2:
            btc_price = btc_data.get('usd', 'N/A')
            btc_change = btc_data.get('usd_24h_change', 0)
            change_class = "crypto-change-positive" if btc_change >= 0 else "crypto-change-negative"
            change_sign = "+" if btc_change >= 0 else ""
            
            st.markdown(f"""
            <h3>Bitcoin (BTC)</h3>
            <div class='crypto-price'>${btc_price:,.2f}</div>
            <div class='{change_class}'>{change_sign}{btc_change:.2f}% (24h)</div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not load current price data: {e}")
# Chat interface
st.markdown("### Chat with your Bitcoin Assistant")
st.markdown("Ask questions about Bitcoin prices, market trends, or request future price predictions.")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
        # Handle prediction charts
        if "prediction_data" in message:
            pred_data = message["prediction_data"]
            
            # Create Plotly figure for prediction visualization
            fig = go.Figure()
            
            # Add historical price line (last 30 days)
            if 'bitcoin' in st.session_state.assistant.crypto_data.historical_data:
                hist_data = st.session_state.assistant.crypto_data.historical_data['bitcoin'].iloc[-30:]
                fig.add_trace(go.Scatter(
                    x=hist_data['date'],
                    y=hist_data['price'],
                    mode='lines',
                    name='Historical Price',
                    line=dict(color='#1E88E5')
                ))
            
            # Add prediction line
            pred_dates = [datetime.datetime.strptime(date, '%Y-%m-%d') for date in pred_data['predicted_dates']]
            fig.add_trace(go.Scatter(
                x=pred_dates,
                y=pred_data['predicted_prices'],
                mode='lines',
                name='Price Prediction',
                line=dict(color='#F7931A', dash='dash')
            ))
            
            # Update layout
            fig.update_layout(
                title=f"Bitcoin Price Prediction - Next {len(pred_dates)} Days",
                xaxis_title="Date",
                yaxis_title="Price (USD)",
                template="plotly_white",
                height=400
            )
            
            # Display the chart
            st.plotly_chart(fig, use_container_width=True)
            
            # Display prediction metrics
            col1, col2, col3 = st.columns(3)
            col1.metric(
                "Current Price", 
                f"${pred_data['current_price']:,.2f}"
            )
            col2.metric(
                f"Predicted ({len(pred_dates)} days)", 
                f"${pred_data['expected_price_after_period']:,.2f}"
            )
            col3.metric(
                "Expected Change", 
                f"{pred_data['predicted_change_percent']:.2f}%",
                delta_color="normal"
            )

# User input
if prompt := st.chat_input("Ask about Bitcoin..."):
    # Add user message
    st.session_state.tool_result = None
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Generate assistant response with spinner
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Process the query
            if any(keyword in prompt.lower() for keyword in ["predict", "forecast", "future", "will be", "next week", "next month", "tomorrow"]):
                # Handle as a prediction query
                days_match = re.search(r'(\d+)\s*(day|days|week|weeks|month|months)', prompt.lower())
                days_ahead = 7  # Default
                
                if days_match:
                    num = int(days_match.group(1))
                    unit = days_match.group(2)
                    
                    if 'week' in unit:
                        days_ahead = num * 7
                    elif 'month' in unit:
                        days_ahead = num * 30
                    else:
                        days_ahead = num
                
                # Limit to reasonable range
                days_ahead = min(max(days_ahead, 1), 30)
                
                # Get prediction
                historical_data = st.session_state.assistant.crypto_data.historical_data['bitcoin']
                prediction = st.session_state.price_predictor.predict_future(historical_data, days_ahead)
                
                if "error" not in prediction:
                    # Create response
                    response = f"""Based on my LSTM model analysis of Bitcoin's historical price data, I forecast:

**Current price:** ${prediction['current_price']:.2f}
**Predicted price in {days_ahead} days:** ${prediction['expected_price_after_period']:.2f}
**Expected change:** {prediction['predicted_change_percent']:.2f}%

I've analyzed price patterns from the historical data to generate this forecast. The prediction chart shows both historical data and the predicted future trend.

*Note: This prediction is based solely on historical price patterns and should not be considered financial advice.*"""
                    
                    st.write(response)
                    
                    # Add visualization
                    # [Same chart code as above]
                    fig = go.Figure()
                    hist_data = historical_data.iloc[-30:]
                    fig.add_trace(go.Scatter(
                        x=hist_data['date'],
                        y=hist_data['price'],
                        mode='lines',
                        name='Historical Price',
                        line=dict(color='#1E88E5')
                    ))
                    
                    pred_dates = [datetime.datetime.strptime(date, '%Y-%m-%d') for date in prediction['predicted_dates']]
                    fig.add_trace(go.Scatter(
                        x=pred_dates,
                        y=prediction['predicted_prices'],
                        mode='lines',
                        name='Price Prediction',
                        line=dict(color='#F7931A', dash='dash')
                    ))
                    
                    fig.update_layout(
                        title=f"Bitcoin Price Prediction - Next {days_ahead} Days",
                        xaxis_title="Date",
                        yaxis_title="Price (USD)",
                        template="plotly_white",
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Store in session with chart data
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "prediction_data": prediction
                    })
                else:
                    response = f"I couldn't generate a price prediction: {prediction['error']}"
                    st.write(response)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
            else:
                # Use standard RAG-based answering
                response = st.session_state.assistant.ask(prompt)
                st.write(response)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })

# User input
 