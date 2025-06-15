# 📄 Example: Bitcoin Prophet Input & Output

This file illustrates a sample input and output for the Bitcoin time series forecasting pipeline using Facebook Prophet.

---

## Input Format (from API)

The dataset is pulled from the CoinGecko API and transformed into the following format for Prophet:

```csv
ds,y
2025-01-01,90123.45
2025-01-02,89500.12
2025-01-03,88342.67

## Forecast Output Format (Prophet)

After training, Prophet produces forecasts in this format:

```csv
ds,yhat,yhat_lower,yhat_upper
2025-05-01,95001.22,93000.58,97050.89
2025-05-02,95325.76,93400.12,97210.30
