# PyCaret_utils.py

import logging
import requests
import pandas as pd
import numpy as np
from pycaret.time_series import setup, compare_models, finalize_model, predict_model

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Wrapper
class CoinGeckoAPI:
    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self):
        self.session = requests.Session()

    def get_ohlc(self, coin_id="bitcoin", vs_currency="usd", days="max"):
        endpoint = f"{self.BASE_URL}/coins/{coin_id}/ohlc"
        params = {"vs_currency": vs_currency, "days": days}

        try:
            response = self.session.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            logger.info(f"Fetched {len(df)} records.")
            return df
        except Exception as e:
            logger.error(f"API Error: {e}")
            raise

def fetch_and_validate_data(client, days=90):
    raw_data = client.get_ohlc(days=days)

    assert isinstance(raw_data, pd.DataFrame)
    assert not raw_data.empty
    assert {'open', 'high', 'low', 'close'}.issubset(raw_data.columns)

    data = raw_data[~raw_data.index.duplicated(keep='first')].copy()
    data['daily_return'] = data['close'].pct_change()
    data['volatility_7d'] = data['daily_return'].rolling(7).std()
    data['volume_ema_14'] = data['close'].ewm(span=14).mean()
    logger.info(f"Data shape after processing: {data.shape}")
    return data

def prepare_data_for_pycaret(data):
    formatted = data[['close']].copy()
    formatted = formatted.asfreq('D').ffill()
    return formatted

def run_pycaret_experiment(data):
    if not isinstance(data.index, pd.DatetimeIndex):
        raise ValueError("Index must be datetime")

    numeric_data = data.select_dtypes(include=np.number).dropna()
    exp = setup(
        data=numeric_data,
        target='close',
        fold_strategy='expanding',
        fold=3,
        numeric_imputation_target='ffill',
        session_id=42,
        fh=7,
        verbose=True
    )
    return exp

def forecast_best_model():
    best_model = compare_models()
    final_model = finalize_model(best_model)
    future_predictions = predict_model(final_model)
    return best_model, future_predictions

def add_lag_features(df, lags=[1, 2, 3]):
    for lag in lags:
        df[f'lag_{lag}'] = df['close'].shift(lag)
    return df.dropna()

# In PyCaret_utils.py
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import plotly.express as px

def create_plotly_dashboard(btc_data, forecast_df, top_models_preds, residuals, filename="bitcoin_dashboard.html"):
    fig = make_subplots(rows=3, cols=1,
                        subplot_titles=("Historical vs Forecast", "Top 3 Model Comparison", "Forecast Residuals"),
                        shared_xaxes=True,
                        vertical_spacing=0.15)

    # 1. Historical vs Forecast
    fig.add_trace(go.Scatter(x=btc_data.index, y=btc_data['close'], name='Historical', line=dict(color='lightgray')),
                  row=1, col=1)

    fig.add_trace(go.Scatter(x=forecast_df.index, y=forecast_df['y_pred'], name='Forecast', mode='lines+markers',
                             line=dict(color='orange')), row=1, col=1)

    # 2. Top 3 Model Comparison
    for model_name, df in top_models_preds.items():
        fig.add_trace(go.Scatter(x=df.index, y=df['y_pred'], name=model_name, mode='lines'), row=2, col=1)

    # 3. Residuals Plot
    fig.add_trace(go.Scatter(x=residuals.index, y=residuals, name='Residuals', mode='lines+markers',
                             line=dict(color='red')), row=3, col=1)

    # Layout
    fig.update_layout(height=1000, width=900, title_text="Bitcoin Forecasting Dashboard", template="plotly_dark")

    # Save to HTML
    import plotly.io as pio
    pio.write_html(fig, file=filename, auto_open=True)

