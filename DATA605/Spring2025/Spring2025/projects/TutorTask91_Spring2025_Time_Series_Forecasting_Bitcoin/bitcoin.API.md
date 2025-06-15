## Project Title:
**Time Series Forecasting of Bitcoin Prices using Prophet**

## Objective:
Build a real-time forecasting pipeline using the Facebook Prophet library on Bitcoin price data fetched via public APIs.

## API Used:
### **CoinGecko API**
- **Endpoint**: `https://api.coingecko.com/api/v3/coins/bitcoin/market_chart`
- **Parameters**:
  - `vs_currency=usd`
  - `days=90`
- **Returns**: Historical market price for the last N days.

## Script Behavior:
- Sends HTTP GET requests using `requests`
- Converts timestamped price values into a Pandas DataFrame
- Outputs `ds` (date) and `y` (price in USD) columns in the correct format for Prophet
- Saves data as a CSV file: `btc_prices.csv`

## Key Libraries:
- `requests` for API access
- `pandas` for preprocessing
- `prophet` for forecasting
- `matplotlib` / `seaborn` for visualization

## Example:
```python
url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart"
params = {"vs_currency": "usd", "days": 90}
response = requests.get(url, params=params)
