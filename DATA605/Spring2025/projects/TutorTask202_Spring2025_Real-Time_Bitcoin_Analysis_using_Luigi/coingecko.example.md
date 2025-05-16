# Coingecko Pipeline Example — End-to-End (6 Tasks)

This file explains the full application using the Coingecko API and a Luigi pipeline.

---

## Goal

- Fetch BTC-USD prices
- Analyze trends
- Detect anomalies
- Plot results
- Email alerts if needed
- Upload to S3

---

## Tasks

1. **FetchDataTask** – Pulls Bitcoin data
2. **CleanDataTask** – Parses/sorts timestamps
3. **AnalyzeDataTask** – Forecast + Z-score
4. **VisualizeDataTask** – Plots price + anomalies, forecast error, volatility, zscore
5. **AlertTask** – Logs + sends email
6. **StoreToS3Task** – Uploads to AWS S3

---

## Outputs

| Task           | Output File                |
|----------------|----------------------------|
| Fetch          | `raw_<date>.json`          |
| Clean          | `clean_<date>.csv`         |
| Analyze        | `analyzed_<date>.csv`      |
| Visualize      | `plot_price_forecast_<date>.png`, `plot_forecast_error_<date>.png`, `plot_volatility_<date>.png`,                `plot_zscore_<date>.png`                      |
| Alert          | `alert_<date>.txt` + email |
| StoreToS3      | Uploads file to S3 bucket  |