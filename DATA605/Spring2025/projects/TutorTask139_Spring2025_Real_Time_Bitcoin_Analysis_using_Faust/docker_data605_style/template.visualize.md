# 📊 Bitcoin Price Visualization

This module plots historical Bitcoin price data with an optional rolling average to help visualize short-term trends and price stability.

---

## 📌 Purpose

To create clean, informative visualizations of:
- Real-time or stored Bitcoin price data
- Rolling averages for trend smoothing
- Future extensions like ARIMA overlays or anomalies

---

## 📂 Input

Assumes a file named `btc_prices.json` with this structure (one JSON per line):

```json
{"timestamp": "2025-05-01 22:30:00", "price": 64200.12}
