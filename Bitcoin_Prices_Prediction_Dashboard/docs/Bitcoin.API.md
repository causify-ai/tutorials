# 📘 Bitcoin Time Series Project – API & Module Documentation

This document explains the architecture and public interface for each Python module used in the project.

---

## 📂 ingestion/fetch.py

### `fetch_bitcoin()`
- Fetches real-time Bitcoin price in USD using CoinGecko API.
- Adds a UTC timestamp.
- Uploads the JSON data to S3 using `s3fs`.

---

## 📂 storage/s3_handler.py

### `upload_json_to_s3(path, data)`
- Writes a JSON dictionary to the specified S3 path.

### `load_json(path)`
- Reads and parses a JSON file from S3.

### `list_data_files(prefix)`
- Lists all files in an S3 folder prefix.

---

## 📂 processing/preprocess.py

### `load_all_btc_data()`
- Loads all JSON price records from S3.
- Converts to a DataFrame, resamples to hourly intervals, interpolates missing values.

---

## 📂 processing/analysis.py

### `decompose_price(df)`
- Performs seasonal decomposition of the 'price' column (trend, seasonality, residual).

### `compute_moving_avg(df, window=12)`
- Adds a moving average column `MA`.

### `detect_anomalies(df, std_dev_thresh=2)`
- Flags anomalies in the `price` column using z-score.

---

## 📂 forecasting/prophet_model.py

### `run_prophet(df)`
- Prepares data and fits Facebook Prophet model.
- Returns DataFrame with forecasted values and confidence intervals.

---

## 📂 visualization/plots.py

### `plot_btc(df)`
- Returns base64-encoded image of raw Bitcoin price trend.

### `plot_ma(df)`
- Returns price vs moving average plot.

### `plot_anomalies(df)`
- Highlights outliers in the price data visually.

---

## 📂 visualization/interactive.py

### `plot_forecast_interactive(forecast_df)`
- Generates HTML-based Plotly chart of forecast.

---

## 🌐 app.py

### `/`
- Renders the Flask dashboard with all visuals and tables.

### `/api/refresh`
- API endpoint to fetch and store the latest price record.

---