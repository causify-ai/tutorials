import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
from prophet import Prophet
from Streamlit_utils import get_current_price, get_historical_data, calculate_moving_average, calculate_technical_indicators, detect_anomalies

# Configure page settings
st.set_page_config(
    page_title="Crypto Dashboard Pro",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}

# Supported cryptocurrencies
CRYPTO_LIST = {
    'bitcoin': 'BTC',
    'ethereum': 'ETH',
    'cardano': 'ADA',
    'solana': 'SOL'
}


def generate_forecast(df, periods=30):
    """
        Generate a price forecast for cryptocurrency based on historical data.

        Args:
            df (pd.DataFrame): Historical price data containing `date` and `price` columns.
            periods (int): Number of future days for which to generate the forecast.

        Returns:
            model (Prophet): Trained Prophet model.
            forecast (pd.DataFrame): Dataframe containing forecasted prices along with upper and lower bounds.
        """
    try:
        df_prophet = df.rename(columns={'date': 'ds', 'price': 'y'})
        model = Prophet(daily_seasonality=True, yearly_seasonality=True)
        model.fit(df_prophet)
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)
        return model, forecast
    except Exception as e:
        st.error(f"Forecast error: {e}")
        return None, None


def get_crypto_news(coin='bitcoin'):
    """
        Fetch the latest news articles related to a specific cryptocurrency.

        Args:
            coin (str): Name of the cryptocurrency (e.g., 'bitcoin').

        Returns:
            list: A list of dictionaries containing the latest news items, including titles, sources, dates, and URLs.
        """
    CryptoPanic_api = os.getenv("CRYPTOPANIC_API_KEY")
    if not CryptoPanic_api:
        st.error("Please set CRYPTOPANIC_API_KEY in your environment.")
    url = f"https://cryptopanic.com/api/v1/posts/?auth_token={CryptoPanic_api}&currencies={CRYPTO_LIST[coin]}"
    try:
        response = requests.get(url)
        news_items = response.json()['results'][:5]  # Get top 5 news items
        return news_items
    except Exception as e:
        st.error(f"You need to add your own news api(CryptoPanic_api) key - Read Streamlit.example.md for more detail instructions")
        return []


def portfolio_manager(coin):
    """
    Provide a user interface to manage the user's cryptocurrency portfolio, including adding amounts and displaying holdings.

    Args:
        coin (str): The selected cryptocurrency (key in CRYPTO_LIST) for portfolio management actions.
    """
    with st.expander("Portfolio Manager"):
        col1, col2 = st.columns(2)
        with col1:
            amount = st.number_input(f"Amount of {CRYPTO_LIST[coin]} to add:", min_value=0.0)
            if st.button("Add to Portfolio"):
                if coin in st.session_state.portfolio:
                    st.session_state.portfolio[coin] += amount
                else:
                    st.session_state.portfolio[coin] = amount
        with col2:
            if coin in st.session_state.portfolio:
                current_value = st.session_state.portfolio[coin] * get_current_price(coin)
                st.metric(f"Your {CRYPTO_LIST[coin]} Holdings",
                          f"{st.session_state.portfolio[coin]:.4f} {CRYPTO_LIST[coin]}",
                          f"${current_value:,.2f}")


def main():
    """
        Main function to initialize and run the Streamlit dashboard for advanced
        cryptocurrency analytics. Features dynamic settings, price tracking,
        historical data analysis, price forecasting using Prophet, and displaying
        the latest market news.
        """

    st.title("💰 Advanced Crypto Analytics Dashboard")

    # Sidebar controls
    with st.sidebar:
        st.header("Settings")
        selected_coin = st.selectbox("Select Cryptocurrency", list(CRYPTO_LIST.keys()))
        days = st.slider("Historical Days", 7, 365, 30)
        ma_window = st.sidebar.selectbox("Moving Average Window", [7, 14, 30])
        forecast_days = st.number_input("Forecast Days", 1, 365, 30)
        anomaly_threshold = st.slider("Anomaly Detection Sensitivity", 1, 5, 3)

    # Current price section
    @st.cache_data(ttl=300)
    def fetch_current_price(coin):
        return get_current_price(coin)

    current_price = fetch_current_price(selected_coin)
    if current_price:
        st.subheader(f"Current {CRYPTO_LIST[selected_coin]} Price: ${current_price:,.2f}")

    # Portfolio manager
    portfolio_manager(selected_coin)

    # Historical data processing

    @st.cache_data(ttl=300)
    def fetch_historical_data(coin, days):
        return get_historical_data(coin, days)
    historical_data = fetch_historical_data(selected_coin, days)
    if not historical_data.empty:

        # Moving Average
        processed_data = calculate_moving_average(historical_data, ma_window)
        fig1 = px.line(
            processed_data,
            x='date',
            y=['price', 'moving_average'],
            labels={'value': 'Price (USD)', 'date': 'Date'},
            title=f"Bitcoin Price Last {days} Days"
        )
        # Technical analysis
        processed_data = calculate_technical_indicators(historical_data)

        # Anomaly detection
        anomaly_data = detect_anomalies(processed_data, anomaly_threshold)

        # Price history chart with technical indicators
        st.subheader("Technical Analysis")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=processed_data['date'], y=processed_data['price'],
                                 name='Price', line=dict(color='gold')))
        fig.add_trace(go.Scatter(x=processed_data['date'], y=processed_data['BB_upper'],
                                 name='Upper Bollinger Band', line=dict(color='gray', dash='dot')))
        fig.add_trace(go.Scatter(x=processed_data['date'], y=processed_data['BB_lower'],
                                 name='Lower Bollinger Band', line=dict(color='gray', dash='dot')))

        # Add anomaly markers
        anomalies = anomaly_data[anomaly_data['anomaly']]
        fig.add_trace(go.Scatter(
            x=anomalies['date'],
            y=anomalies['price'],
            mode='markers',
            marker=dict(color='red', size=8),
            name='Anomaly'
        ))

        fig.update_layout(
            title=f"{CRYPTO_LIST[selected_coin]} Price with Technical Indicators",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.plotly_chart(fig1, use_container_width=True)

        # Technical indicators subplots
        st.subheader("Momentum Indicators")
        col1, col2 = st.columns(2)
        with col1:
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=processed_data['date'], y=processed_data['RSI'],
                                         name='RSI', line=dict(color='purple')))
            fig_rsi.add_hline(y=30, line_dash="dot", line_color="green")
            fig_rsi.add_hline(y=70, line_dash="dot", line_color="red")
            fig_rsi.update_layout(title="Relative Strength Index (RSI)")
            st.plotly_chart(fig_rsi, use_container_width=True)

        with col2:
            fig_macd = go.Figure()
            fig_macd.add_trace(go.Scatter(x=processed_data['date'], y=processed_data['MACD'],
                                          name='MACD', line=dict(color='blue')))
            fig_macd.add_trace(go.Scatter(x=processed_data['date'], y=processed_data['MACD_signal'],
                                          name='Signal Line', line=dict(color='orange')))
            fig_macd.update_layout(title="MACD")
            st.plotly_chart(fig_macd, use_container_width=True)

        # Forecasting section
        st.subheader("Price Forecasting")
        if st.button("Generate Forecast"):
            with st.spinner("Training forecast model..."):
                model, forecast = generate_forecast(historical_data, forecast_days)

            if forecast is not None:
                fig_forecast = go.Figure()
                fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'],
                                                  name='Predicted Price', line=dict(color='limegreen')))
                fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'],
                                                  line=dict(color='gray', dash='dot'), name='Upper Bound'))
                fig_forecast.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'],
                                                  line=dict(color='gray', dash='dot'), name='Lower Bound'))
                fig_forecast.update_layout(
                    title=f"{forecast_days}-Day Price Forecast",
                    xaxis_title="Date",
                    yaxis_title="Price (USD)"
                )
                st.plotly_chart(fig_forecast, use_container_width=True)

                # Show forecast components
                st.subheader("Forecast Components")
                components_fig = model.plot_components(forecast)
                st.pyplot(components_fig)

        # News section
        st.subheader("Latest Market News")
        news_items = get_crypto_news(selected_coin)
        for item in news_items:
            with st.expander(item['title']):
                st.markdown(f"**Source:** {item['source']['title']}")
                st.write(item['created_at'][:10])
                st.write(item['url'])


if __name__ == "__main__":
    main()
