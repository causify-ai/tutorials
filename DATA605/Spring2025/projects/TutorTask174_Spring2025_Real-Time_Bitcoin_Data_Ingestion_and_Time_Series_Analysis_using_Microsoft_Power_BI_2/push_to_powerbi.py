# push_to_powerbi.py

import requests
import pandas as pd
from prophet import Prophet
from datetime import datetime

# Load your input CSV file (this must exist and be updated with new data)
df = pd.read_csv("bitcoin_price_transformed.csv")

# Prepare data for Prophet
df_prophet = df[['timestamp', 'price_usd']].copy()
df_prophet.columns = ['ds', 'y']
df_prophet['ds'] = pd.to_datetime(df_prophet['ds'])

# Train Prophet model
model = Prophet()
model.fit(df_prophet)

# Predict next 60 minutes
future = model.make_future_dataframe(periods=60, freq='min')
forecast_prophet = model.predict(future)

# Add 7-minute moving average to forecast
forecast_prophet['moving_avg_price'] = forecast_prophet['yhat'].rolling(window=7).mean()

# Compute % change (optional: based on yhat)
forecast_prophet['price_change_pct'] = forecast_prophet['yhat'].pct_change().fillna(0) * 100

# Select only the last 60 forecasted rows
forecast_tail = forecast_prophet.tail(60)[['ds', 'yhat', 'moving_avg_price', 'price_change_pct']]

# Convert to Power BI-compatible format
rows = []
for _, row in forecast_tail.iterrows():
    rows.append({
        "timestamp": row['ds'].strftime('%Y-%m-%dT%H:%M:%SZ'),
        "price_usd": float(row['yhat']),
        "moving_avg_price": float(row['moving_avg_price']),
        "price_change_pct": float(row['price_change_pct'])
    })

# Your actual streaming dataset URL
push_url = "https://api.powerbi.com/beta/ee2d6d72-9535-4242-a077-acf185782f9b/datasets/afbad650-0150-4703-bbb9-e046dec7b061/rows?experience=power-bi&key=oLBJptO3M8eQMVxjI%2BZjy7cSfNhuR%2BjRfNLqCXwmSq9ux6%2FeN422pmpaeVTj5QCLMtndCH4bACN1zNDJixYt1w%3D%3D"

# Send the data
response = requests.post(push_url, json=rows)
print(rows[:5])  # preview a few rows

if response.ok:
    print("✅ Forecast pushed!")
else:
    print(f"❌ Push failed: {response.status_code}")
