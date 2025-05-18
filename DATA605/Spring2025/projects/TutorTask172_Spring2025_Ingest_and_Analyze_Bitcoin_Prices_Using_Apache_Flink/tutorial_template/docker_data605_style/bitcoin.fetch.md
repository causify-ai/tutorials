# bitcoin.fetch.md — Example Application Using the API Layer

This example demonstrates a complete end-to-end use case of the Bitcoin API layer defined in `bitcoin_utils.py`. It integrates live Bitcoin streaming, historical data fetching, forecasting, and visualization.

---

## 🔁Step 1: Real-Time Bitcoin Price Streaming

We create a PyFlink streaming job that consumes Bitcoin prices from the BitcoinPriceSource generator. The class tracks a rolling price window, computes real-time metrics, and logs both raw prices and computed statistics to InfluxDB.

```python
from pyflink.datastream import StreamExecutionEnvironment
from bitcoin_utils import BitcoinPriceSource
from pyflink.common.typeinfo import Types

env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)

source = BitcoinPriceSource(interval_sec=30, window_size=10)

ds = env.from_collection(
    collection=source,
    type_info=Types.TUPLE([Types.LONG(), Types.FLOAT()])
)

ds.print()
env.execute("Bitcoin Stats Streaming Job")
```

Each streaming record prints:
- Current Bitcoin price
- Moving average (MA)
- Standard deviation
- Exponential moving average (EMA)
- Max/Min in window
- 24h percent change
- InfluxDB logs with timestamp

---

## Step 2: Fetch Historical Data

Use the Yahoo Finance API via `yfinance` to fetch daily Bitcoin price history for training the forecasting model.

```python
from bitcoin_utils import fetch_historical_data

btc_data = fetch_historical_data()
btc_data.head()
```

This produces a DataFrame with:
- `ds`: Date
- `y`: Closing price

---

##  Step 3: Train NeuralProphet Forecasting Model

```python
from bitcoin_utils import train_neural_prophet_model

model = train_neural_prophet_model(btc_data)
```

This creates a Prophet model trained on historical price data, using daily and yearly seasonality components.

---

##  Step 4: Generate Forecast

Forecast Bitcoin prices for the next 365 days:

```python
from bitcoin_utils import make_forecast

forecast = make_forecast(model, btc_data, periods=365)

```

This returns a DataFrame containing forecasted values (`yhat`) and confidence intervals (`yhat_lower`, `yhat_upper`).

---

##  Step 5: Plot Forecast & Components

```python
from bitcoin_utils import plot_forecast, plot_components

plot_forecast(model, forecast)
plot_components(model, forecast)
```

- `plot_forecast` plots the full time series including forecast
- `plot_components` shows trend, weekly, and yearly seasonality

---

## Step 6: View Forecast for the Next 7 Days

Filter and print only the next week of forecasted prices beyond the historical date range:

```python
last_date = btc_data['ds'].max()
future_forecast = forecast[forecast['ds'] > last_date]

print("Bitcoin price forecast for next 7 days:")
print(future_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].head(7))
```

---

##  Summary

-This example demonstrated how to:

-Stream real-time Bitcoin prices using BitcoinPriceSource

-Store metrics in InfluxDB

--Fetch historical data via Yahoo Finance

Train a NeuralProphet model on closing prices

--Forecast future Bitcoin prices with daily/yearly seasonality

-Visualize full forecasts and seasonal trends

All logic is modularized in `bitcoin_utils.py` and can be reused for larger crypto analytics pipelines or dashboards.
