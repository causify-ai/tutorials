import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
from prophet.plot import plot_components_plotly
import plotly.graph_objs as go
import joblib
import os
from sklearn.metrics import mean_squared_error, mean_absolute_error, mean_absolute_percentage_error
from datetime import timedelta

# === UI Configuration ===
st.set_page_config(page_title=" Bitcoin Forecast Dashboard", layout="wide")
st.markdown("""
    <style>
    body { background-color: #F9FAFB; color: #111827; font-family: 'Segoe UI', sans-serif; }
    .stSidebar { background-color: #F0F4F8; border-right: 1px solid #E0E0E0; }
    .stButton>button {
        width: 100%; background-color: #3B82F6; color: white; border-radius: 8px; font-weight: 600; height: 40px;
    }
    .stMetricLabel { color: #111827; }
    .big-font { font-size:30px !important; font-weight: bold; text-align: center; }
    h1, h2, h3, h4 { color: #1D4ED8; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# === Heading Above Image ===
st.markdown("<h1> Bitcoin Forecast Dashboard</h1>", unsafe_allow_html=True)

# === Image Title and Banner ===
image_path = "/home/dhruvyellanki/src/tutorials1/DATA605/Spring2025/projects/TutorTask137_Spring2025_Bitcoin_Forecasting_with_Facebook_Prophet/images/btc_image.jpeg"
if os.path.exists(image_path):
    st.image(image_path, use_container_width=True)

# === Load Dataset and Model ===
data_path = 'data/bitcoin_data_df.csv'
model_path = 'model/prophet_btc_model.pkl'

if not os.path.exists(data_path) or not os.path.exists(model_path):
    st.error(" Data or Model file not found. Please check the paths.")
    st.stop()

bitcoin_df = pd.read_csv(data_path, parse_dates=['ds'])
bitcoin_df.sort_values('ds', inplace=True)
model = joblib.load(model_path)

# === Add Regressors ===
bitcoin_df['doubling_flag'] = bitcoin_df['ds'].isin(pd.to_datetime(['2013-11-29', '2017-12-17', '2021-04-14', '2021-11-10', '2024-03-20'])).astype(int)
bitcoin_df['volatility_flag'] = bitcoin_df['ds'].isin(pd.to_datetime(['2013-04-10', '2017-12-22', '2020-03-12'])).astype(int)
bitcoin_df['etf_approval_flag'] = bitcoin_df['ds'].isin(pd.to_datetime(['2021-10-19'])).astype(int)
bitcoin_df['exchange_crash_flag'] = bitcoin_df['ds'].isin(pd.to_datetime(['2022-11-08'])).astype(int)
bitcoin_df['rolling_volatility'] = bitcoin_df['y'].rolling(30).mean().fillna(method='bfill').fillna(method='ffill')

# === Sidebar Controls ===
st.sidebar.markdown("### Forecast Controls")
forecast_years = 5
forecast_days = forecast_years * 365
selected_year = st.sidebar.selectbox("Filter by Year", sorted(bitcoin_df['ds'].dt.year.unique(), reverse=True))
selected_month = st.sidebar.selectbox("Filter by Month", ['All'] + list(bitcoin_df['ds'].dt.month_name().unique()))
selected_date = st.sidebar.date_input(" Forecast for Specific Date", pd.Timestamp.today())

# === Forecast Preparation ===
cutoff_date = bitcoin_df['ds'].max() - timedelta(days=forecast_days)
bitcoin_test_df = bitcoin_df[bitcoin_df['ds'] >= cutoff_date]

future = model.make_future_dataframe(periods=forecast_days)
future = future.merge(bitcoin_df[['ds', 'doubling_flag', 'volatility_flag', 'etf_approval_flag', 'exchange_crash_flag', 'rolling_volatility']], on='ds', how='left')
future.fillna(method='ffill', inplace=True)
forecast = model.predict(future)
forecast.set_index('ds', inplace=True)
bitcoin_test_df.set_index('ds', inplace=True)

common_dates = forecast.index.intersection(bitcoin_test_df.index)
predicted = forecast.loc[common_dates, 'yhat'].values
actual = bitcoin_test_df.loc[common_dates, 'y'].values

rmse = np.sqrt(mean_squared_error(actual, predicted))
mae = mean_absolute_error(actual, predicted)
mape = mean_absolute_percentage_error(actual, predicted) * 100


# === BTC Prices Table ===
st.markdown("### BTC Prices: Today & Next 30 Days")
next_30_days = forecast.reset_index().loc[forecast.index >= pd.Timestamp.today(), ['ds', 'yhat']].head(30)
next_30_days.columns = ['Date', 'Predicted Price']
st.dataframe(next_30_days.style.format({'Predicted Price': '${:,.2f}'}))

csv_download = next_30_days.to_csv(index=False)
st.download_button(" Download 30-Day Forecast", data=csv_download, file_name="btc_next_30_days.csv", mime="text/csv")

# === Trend Analysis ===
st.markdown("### Trend Analysis")
if selected_month != 'All':
    month_df = bitcoin_df[bitcoin_df['ds'].dt.month_name() == selected_month]
else:
    month_df = bitcoin_df

fig_trend = go.Figure()
fig_trend.add_trace(go.Scatter(x=month_df['ds'], y=month_df['y'], mode='lines', name='BTC Price', line=dict(color='#6366F1', width=2)))
fig_trend.update_layout(title=f" BTC Price Trend - {selected_month} {selected_year}", template='plotly_white', hovermode='x unified')
st.plotly_chart(fig_trend, use_container_width=True)

# === Long-Term Forecast Trend ===
st.markdown("### Long-Term BTC Trend with Forecast")
fig_long_term = go.Figure()
fig_long_term.add_trace(go.Scatter(
    x=bitcoin_df['ds'], y=bitcoin_df['y'],
    mode='lines', name='Actual Price', line=dict(color='#10B981', width=2)
))
fig_long_term.add_trace(go.Scatter(
    x=forecast.reset_index()['ds'], y=forecast.reset_index()['yhat'],
    mode='lines', name='Forecast', line=dict(color='#3B82F6', width=2, dash='dash')
))
fig_long_term.update_layout(
    title=" Actual vs Forecasted BTC Price (Full Timeline)",
    xaxis_title="Date",
    yaxis_title="Price (USD)",
    template="plotly_white",
    hovermode="x unified"
)
st.plotly_chart(fig_long_term, use_container_width=True)


# === Forecast for Selected Date  ===
st.markdown("### Forecast for Selected Date")
forecast_date_data = forecast.loc[forecast.index == pd.to_datetime(selected_date)]
if not forecast_date_data.empty:
    yhat = forecast_date_data['yhat'].values[0]
    st.markdown(f"""
        <div style="background-color: #E0F2FE; padding: 20px; border-radius: 8px; text-align: center; border-left: 6px solid #3B82F6;">
            <h3 style="color: #1D4ED8;">Date: {selected_date}</h3>
            <h2 style="color: #111827;">Predicted Price: ${yhat:,.2f}</h2>
        </div>
    """, unsafe_allow_html=True)
else:
    st.warning("No forecast data available for the selected date.")

# === Prophet Components Plot ===
st.markdown("### Prophet Components Analysis")
fig_components = plot_components_plotly(model, forecast.reset_index())
st.plotly_chart(fig_components, use_container_width=True)

# === Articles Section ===
st.markdown("### Articles: The Defining Moments of Bitcoin")

articles = [
    (" 2013 Bull Run: Bitcoin Hits $1,150",
     "**Date:** December 1, 2013  \nIn 2013, Bitcoin captured global attention for the first time as its price soared to **1,150 dollars**. This remarkable rise was largely driven by surging demand from Asian markets, particularly China, and a flurry of positive media coverage. However, this bull run also raised red flags about regulatory oversight and the sustainability of such rapid growth. It set the tone for Bitcoin’s emerging reputation as both a revolutionary financial asset and a highly volatile investment."),
    
    (" 2014 Mt. Gox Collapse: The First Major Bear Market",
     "**Date:** February 1, 2014  \nThe euphoria of 2013 came crashing down when **Mt. Gox**, the largest Bitcoin exchange at the time, collapsed after losing **850,000 BTC**—worth nearly **450 million dollars** then. This incident exposed serious flaws in crypto exchange security and transparency. The aftermath sent shockwaves through the market, eroding investor confidence and causing Bitcoin’s price to plummet below **$300**, marking its first major bear market."),
    
    (" 2017 All-Time High: The ICO Boom",
     "**Date:** December 1, 2017  \nFueled by the Initial Coin Offering (ICO) craze, Bitcoin skyrocketed to nearly **20,000 dollars** by the end of 2017. Retail investors rushed in, driven by the belief that blockchain technology would revolutionize industries and bring massive profits. However, this speculative frenzy was unsustainable. As many ICO projects turned out to be scams or failed ventures, regulatory bodies cracked down, and the market bubble burst, sending prices sharply lower."),
    
    (" 2018 Crypto Winter: Harsh Reality Sets In",
     "**Date:** December 1, 2018  \nFollowing the 2017 crash, Bitcoin entered a prolonged bear market known as the **Crypto Winter**. Over the course of 2018, prices steadily declined, bottoming out near **3,200 dollars**. This period was marked by skepticism about the future of cryptocurrencies, widespread project failures, and significant investor losses. However, it also became a time of reflection and rebuilding for serious projects focused on long-term viability."),
    
    (" 2020 COVID-19 Crash: Global Financial Panic",
     "**Date:** March 1, 2020  \nThe onset of the COVID-19 pandemic triggered a massive sell-off across global markets, and Bitcoin wasn’t spared. On **Black Thursday**, Bitcoin’s value plummeted by over **40%** in a single day, falling below **4,000 dollars**. Despite this sharp decline, unprecedented fiscal and monetary stimulus measures by governments reignited interest in Bitcoin as a hedge against inflation. This paved the way for a swift recovery and the next bull run."),
    
    (" 2020 Halving Event: The Supply Squeeze",
     "**Date:** May 1, 2020 \nBitcoin’s third halving reduced mining rewards from **12.5 BTC to 6.25 BTC** per block, effectively cutting the rate at which new Bitcoins entered circulation. Historically, halvings have been a precursor to major bull markets due to the reduced supply pressure. True to form, the 2020 halving initiated another upward price cycle, supported by growing institutional interest and the perception of Bitcoin as digital gold."),
    
    (" 2021 Bull Run (April): Institutional FOMO and Coinbase IPO",
     "**Date:** April 1, 2021  \nBitcoin’s price surged past **60,000 dollars** in early 2021, fueled by unprecedented institutional demand and the landmark **Coinbase IPO**. This period saw major companies like Tesla and MicroStrategy adding Bitcoin to their balance sheets. The growing belief in Bitcoin’s long-term value as a hedge against inflation and a store of value drove market optimism to new heights."),
    
    (" 2021 Bull Run (November): Bitcoin Hits 69,000 dollars ATH",
     "**Date:** November 1, 2021  \nBitcoin reached its **all-time high of nearly 69,000 dollars** following the approval of the first Bitcoin futures ETFs in the United States. This milestone was a significant validation of Bitcoin’s legitimacy in the eyes of institutional investors. Massive inflows from hedge funds and investment firms further fueled this record-breaking rally, though it was soon followed by increased volatility."),
    
    (" 2022 FTX Collapse: Trust in Crypto Shattered Again",
     "**Date:** November 1, 2022  \nJust as the market was stabilizing, the shocking collapse of **FTX**, one of the largest cryptocurrency exchanges, devastated investor confidence. The collapse revealed fraudulent practices and poor financial management, triggering billions in losses across the crypto ecosystem. Bitcoin’s price plummeted below **16,000 dollars**, ushering in another painful bear market phase."),
    
    (" 2024 Halving Event: Anticipating the Next Bull Run",
     "**Date:** April 1, 2024  \nThe most recent halving event reduced Bitcoin’s block rewards to **3.125 BTC**. As history has shown, this supply reduction often leads to bullish price momentum in the following months or years. With stronger institutional infrastructure, clearer regulations, and increased mainstream acceptance, many investors are optimistic that this halving could trigger Bitcoin’s next major rally.")]


for title, content in articles:
    st.subheader(title)
    st.markdown(content)
    st.markdown("---")


# === Forecast Data Table ===
st.markdown("### Raw Complete Forecast Data")
raw_forecast_df = forecast.reset_index()[['ds', 'yhat']]
raw_forecast_df.columns = ['Date', 'Predicted Price']
st.dataframe(raw_forecast_df.style.format({'Predicted Price': '${:,.2f}'}))
