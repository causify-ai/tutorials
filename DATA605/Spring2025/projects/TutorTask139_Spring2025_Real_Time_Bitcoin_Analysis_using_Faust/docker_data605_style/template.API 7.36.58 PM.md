# 📡 Real-Time Bitcoin Price Fetcher

This module fetches live Bitcoin price data from the [CoinGecko API](https://www.coingecko.com/en/api) in real-time.

## 📌 Purpose
To continuously retrieve the current price of Bitcoin in USD for downstream processing and analysis using Faust.

---

## ⚙️ Functionality

### `fetch_bitcoin_price()`
- **Description**: Fetches the latest price of Bitcoin from CoinGecko.
- **Returns**: A dictionary containing:
  - `timestamp` – current system time
  - `price` – current BTC price in USD
- **Prints**: Formatted price output in console.

---

## ▶️ Usage

### 🧪 One-time fetch (for testing):
```python
fetch_bitcoin_price()
