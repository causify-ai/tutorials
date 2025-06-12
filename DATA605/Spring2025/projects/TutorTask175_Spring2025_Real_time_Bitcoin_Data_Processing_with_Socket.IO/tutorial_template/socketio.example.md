# Real-Time Bitcoin Price Simulation using python-socketio

This example demonstrates a simulated real-time Bitcoin price streaming system using `python-socketio`, `NumPy`, `Pandas`, and `Plotly`. It showcases how a real-time data dashboard could be built using Socket.IO — even without a live WebSocket connection.

---

## 🎯 Objective

To simulate real-time Bitcoin price updates, apply basic time series analysis, and visualize results through an interactive dashboard using Plotly.

---

## 🔄 Project Workflow

### 1. Price Simulation

- The `simulate_fake_btc_stream()` function in `socketio_utils.py` generates BTC prices using small random fluctuations.
- This emulates how a live WebSocket data stream would behave in production.

### 2. Time Series Analysis

- A 5-point Simple Moving Average (SMA) is calculated using the `compute_sma()` function.
- This analysis helps smooth short-term volatility and reflect trend direction.

### 3. Real-Time Visualization

- Prices and SMA are dynamically plotted using **Plotly**.
- The chart simulates a live financial dashboard experience by refreshing with each stream event.

---

## 🛠️ Technologies Used

| Component         | Tool/Library               |
|------------------|----------------------------|
| Data Simulation   | `simulate_fake_btc_stream()` |
| Analytics         | `NumPy`, `Pandas`          |
| Visualization     | `Plotly`                   |
| Real-time Support | `python-socketio`          |

---

## 🌐 Real-World Application

If connected to a real WebSocket API (like CoinCap or Binance), this architecture could:

- Push Bitcoin price updates to a frontend dashboard
- Track and visualize trends in real-time
- Enable real-time anomaly detection or alerting

---

## ⚠️ Limitations

- This project uses **simulated prices** to avoid hitting rate limits (e.g., HTTP 429) on public APIs.
- A frontend component was not implemented, but the backend simulation is fully functional and ready for integration.

---

## ✅ Conclusion

This example illustrates how `python-socketio` can support real-time data processing pipelines. By combining simulated streaming with analytical techniques and interactive charts, it lays the groundwork for building robust live financial dashboards.
