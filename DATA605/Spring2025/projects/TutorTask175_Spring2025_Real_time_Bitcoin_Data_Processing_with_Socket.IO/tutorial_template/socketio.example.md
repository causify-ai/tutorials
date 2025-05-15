# Real-Time Bitcoin Price Simulation using python-socketio

This example demonstrates a simulated real-time Bitcoin price streaming system using `python-socketio`, `NumPy`, `Pandas`, and `Plotly`. It showcases how a real-time data dashboard could be built using Socket.IO, even without connecting to a real WebSocket data feed.

---

## Objective

The goal of this project is to simulate real-time Bitcoin price updates, apply basic time series analysis, and display the results using an interactive Plotly chart.

---

## Project Workflow

### 1. Price Simulation

- A function `simulate_fake_btc_stream()` in `socketio_utils.py` simulates BTC prices using small random fluctuations.
- This mimics how a real WebSocket data stream would behave over time.

### 2. Time Series Analysis

- We calculate a 5-point **Simple Moving Average (SMA)** using the `compute_sma()` function.
- This helps smooth price trends and demonstrate how basic analytics would be applied to a live stream.

### 3. Visualization

- The prices and SMA are plotted using **Plotly**.
- The chart updates each time new data is simulated.
- It gives users a feel of what a real-time financial dashboard could look like.

---

## Technologies Used

| Component               | Library / Tool          |
|-------------------------|--------------------------|
| Simulation              | `simulate_fake_btc_stream()` |
| Data Processing         | `NumPy`, `Pandas`       |
| Visualization           | `Plotly`                |
| API Architecture        | `python-socketio`       |

---

## Real-World Relevance

If connected to a live WebSocket price feed (e.g., from CoinCap or Binance), this architecture could be used to:

- Push updates to a frontend dashboard
- Track Bitcoin in real-time
- Analyze trends and detect anomalies on the fly

---

## Limitations

- We used **simulated prices** instead of live data due to rate limiting (HTTP 429 errors).
- The current setup does **not include a frontend client**, but the backend is ready for integration.

---

## Conclusion

This example illustrates how `python-socketio` can support real-time data pipelines, especially when combined with streaming simulation and visual analytics. It forms the foundation of a live financial dashboard architecture.
