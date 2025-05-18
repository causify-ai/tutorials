# 📘 API Documentation: Real-Time Bitcoin Price Analysis

## 🧩 Native API: CoinGecko

- **Name:** CoinGecko API
- **Base URL:** `https://api.coingecko.com/api/v3`
- **Main Endpoint Used:**  
  `/simple/price?ids=bitcoin&vs_currencies=usd`
- **Function:**  
  Returns the current price of Bitcoin in USD.

### ✅ Example Native API Call

```http
GET https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd
```
 
### ✅ Example Response

```json
{
  "bitcoin": {
    "usd": 103452.77
  }
}
```

---

## 🛠️ Software Layer: FastAPI Application

### 📂 Endpoint: `/dashboard` (GET)

- **Path:** `http://localhost:8000/dashboard`
- **Method:** GET
- **Purpose:** 
  - Fetch and display the real-time Bitcoin price (via CoinGecko)
  - Display a 1-year interactive price chart (via Plotly)

### 🔁 Internal Logic Flow

1. **Live Data Fetching:**  
   Calls CoinGecko’s native endpoint to get current price.

2. **Historical Data Load:**  
   Loads past 365 days of Bitcoin prices from `bitcoin_5yr_history.csv` (generated via CoinGecko and saved locally).

3. **Data Processing:**  
   - Computes a 30-day moving average.
   - Prepares a DataFrame for visualization.

4. **Chart Generation:**  
   Uses Plotly to render a styled, interactive chart showing:
   - Daily Bitcoin prices
   - 30-day trend line

5. **HTML Response:**  
   Combines real-time price + chart in a single HTML response, styled in dark mode.

---

## ⚙️ Dependencies Used

- `FastAPI`: for creating the web server and endpoint
- `httpx`: to call CoinGecko API asynchronously
- `pandas`: to manage historical price data
- `plotly`: to create interactive charts
- `uvicorn`: to serve the FastAPI app

---

## 🔐 Rate Limits / Access Notes

- The free CoinGecko API allows:
  - ~50 calls/minute (rate limits apply)
  - Only 365 days of historical data without a paid plan

---

## 🧪 Testing the Endpoint

1. Start the app:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Visit:
   ```
   http://localhost:8000/dashboard
   ```

You will see:
- 🟡 Live BTC price (fetched at that moment)
- 📈 Interactive 1-year chart (loaded from saved CSV)