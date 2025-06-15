# Customer.io Event Data Analysis

<!-- toc -->

- [Project description](#project-description)
  * [Table of Contents](#table-of-contents)
    + [Hierarchy](#hierarchy)
  * [General Guidelines](#general-guidelines)
  * [Notebook Summary](#notebook-summary)
    + [1. Data Retrieval and Aggregation](#1-data-retrieval-and-aggregation)
    + [2. Visual Trend Analysis](#2-visual-trend-analysis)
    + [3. Spike Detection](#3-spike-detection)
    + [4. Forecasting with ARIMA](#4-forecasting-with-arima)
    + [5. Anomaly Detection (Z-Score)](#5-anomaly-detection-z-score)
  * [Evaluation Metrics](#evaluation-metrics)
  * [References](#references)

<!-- tocstop -->

## Project description

A time series analysis pipeline built to evaluate **Customer.io behaviors** such as `email_opened`, `clicked`, and `app_login`. This project uses statistical methods (e.g., z-score), time-series forecasting (ARIMA), and visualizations to derive actionable insights from user engagement trends.

---


## General Guidelines

- This notebook demonstrates how to analyze and forecast engagement metrics using event data from Customer.io.
- Architecture:
  - Input: Preprocessed behavior log (`from simulated_event_log.csv`)
  - Processing:
    - Aggregation to daily and weekly level
    - Spike and anomaly detection (mean±2std, z-score)
    - ARIMA model for short-term forecasting
- Output: Plots of trends, spike annotations, and ARIMA accuracy scores.
- File follows naming convention: `Customerio_Event_Data.example.ipynb`

---

## Notebook Summary

### 1. Data Retrieval and Aggregation
- Events are retrieved via a utility function and grouped by date.
- Daily and weekly counts are computed using `resample()`.

### 2. Visual Trend Analysis
- Daily and weekly trends are visualized.
- Observed stable but noisy daily counts; weekly counts show smoother patterns.

### 3. Spike Detection
- Spikes in `email_opened` are flagged using:
  ```python
  threshold = mean + 2 * std
  ```
- Detected spikes on high-engagement days (e.g., 2025-01-27).

### 4. Forecasting with ARIMA
- Applied ARIMA on each event type.
- Flat forecasts captured general level but struggled with fluctuations.
- Best performance on `email_opened` (MAE: 6.20, RMSE: 7.14)

### 5. Anomaly Detection (Z-Score)
- Z-scores used to identify statistically significant highs/lows.
- Anomalies detected both for high spikes and sharp drops.
- Example:

| Date       | Count | Z-Score | Type        |
|------------|-------|---------|-------------|
| 2025-03-05 | 109   | +2.62   | High spike  |
| 2025-12-11 | 56    | -2.87   | Sharp drop  |

---

## Evaluation Metrics

| Event        | MAE   | RMSE  | Interpretation           |
|--------------|-------|-------|---------------------------|
| email_opened | 6.20  | 7.14  |  Best performance  |
| app_login    | 9.32  | 10.02 |  Moderate, missed spikes   |
| clicked      | 9.82  | 11.61 |  Struggled with volatility  |

---

## References

- [README Guidelines](/DATA605/DATA605_Spring2025/README.md)
- `Customerio_Event_Data_utils.py`
- Notebook file: `Customerio.example.ipynb`
