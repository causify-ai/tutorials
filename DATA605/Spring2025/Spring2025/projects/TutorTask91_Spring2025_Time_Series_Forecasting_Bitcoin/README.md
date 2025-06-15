# Bitcoin Price Forecasting using Facebook Prophet

**Author:** Vihaan Shah
**Course:** DATA605 - Spring 2025
**Project:** Time Series Forecasting

---

## Abstract

This project applies Facebook's open-source time series forecasting tool, Prophet, to predict short-term Bitcoin prices. Using data pulled from the CoinGecko API, we demonstrate preprocessing, model training, forecasting, and evaluation using real-world cryptocurrency data. The goal is to accurately model price trends while accounting for daily, weekly, and holiday effects.

---

## Dataset

* **Source:** CoinGecko API
* **Attributes Used:**

  * `timestamp` (converted to datetime)
  * `price` (in USD)
* **Time Range:** Last 90 days
* **Frequency:** Daily

---

## Forecasting Methodology

We used the Facebook Prophet model with the following configuration:

* Included daily and weekly seasonality
* Added holidays to test their impact on Bitcoin pricing
* Split dataset into training and test subsets
* Evaluated forecast accuracy using MAE and RMSE

---

## Key Steps and Code Highlights

1. **Data Collection:**

   * Fetched Bitcoin price data using CoinGecko's `/market_chart` endpoint.

2. **Data Preprocessing:**

   * Converted timestamps to `datetime` format
   * Renamed columns to Prophet-compatible (`ds`, `y`)

3. **Model Building:**

   * Used Prophet with default plus custom seasonalities
   * Modeled with and without holidays

4. **Visualization:**

   * Forecast plot (next 30 days)
   * Trend, weekly, and daily decomposition plots
   * Holiday effects comparison

5. **Evaluation:**

   * MAE: 2408.12
   * RMSE: 2806.25

---

## Results & Observations

* **30-Day Forecast:** Showed upward momentum in Bitcoin prices from mid-April to mid-June.
* **Trend Plot:** Indicated a dip around March with expected recovery later.
* **Seasonality:**

  * Weekly peaks seen mid-week (Thursday/Friday)
  * Daily variation showed notable highs and lows at certain hours
* **Holiday Effects:** Slight impact observed around specific dates, confirming some influence

---

## Conclusion

The Facebook Prophet model effectively captured nonlinear Bitcoin price trends and demonstrated interpretable seasonality patterns. While the RMSE and MAE indicate room for improvement, the model shows strong potential for real-time forecasting with further tuning. The project highlights the viability of combining public APIs, data science tools, and time series models to forecast complex, volatile financial instruments like cryptocurrency.

---

## Future Enhancements

* Tune hyperparameters (e.g., changepoint prior scale)
* Compare with other models like ARIMA or LSTM
* Incorporate additional features like trading volume or sentiment scores

---
