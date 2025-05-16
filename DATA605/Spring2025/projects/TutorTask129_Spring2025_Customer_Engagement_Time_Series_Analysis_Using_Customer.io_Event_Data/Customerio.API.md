# Customer.io API Tutorial

<!-- toc -->

- [Tutorial Template for Native API of the tool used](#tutorial-template-for-native-api-of-the-tool-used)
  * [Table of Contents](#table-of-contents)
    + [Hierarchy](#hierarchy)
  * [General Guidelines](#general-guidelines)
  * [Notebook Summary](#notebook-summary)
    + [1. Context and Setup](#1-context-and-setup)
    + [2. Simulating and Uploading Data](#2-simulating-and-uploading-data)
    + [3. Event Summary and Aggregation](#3-event-summary-and-aggregation)
    + [4. Trend Analysis and Spike Detection](#4-trend-analysis-and-spike-detection)
    + [5. Forecasting and Anomaly Detection](#5-forecasting-and-anomaly-detection)
  * [Remarks on API Use](#remarks-on-api-use)
  * [References](#references)

<!-- tocstop -->

## Tutorial Template for Native API of the tool used

This tutorial demonstrates how to simulate and analyze user interaction events using the **native API of Customer.io**. Since Customer.io's platform currently only **allows data upload through API and restricts data retrieval** (due to privacy constraints), this project includes a simulation layer to emulate full event interaction logs.

---


## General Guidelines

- This tutorial is part of the `DATA605` coursework.
- It follows the conventions outlined in [README](/DATA605/DATA605_Spring2025/README.md).
- Describes Customer.io's API functionality through `template.API.ipynb`.
- File naming follows: `customerio.API.md`

---

## Notebook Summary

### 1. Context and Setup

- API credentials (`SITE_ID`, `API_KEY`) are used to authenticate with the Customer.io API.
- The `customerio` Python SDK and `faker` are used to generate mock user data.

### 2. Simulating and Uploading Data

Due to the **one-directional design of Customer.io's API**, we simulate users and events locally and push them to the platform:

- **User Simulation**: 1000 users created using `faker.uuid4()`, fake names, and emails.
- **Event Simulation**:
  - Events: `email_opened`, `clicked`, `app_login`
  - Campaigns: `"Spring Sale"`, `"Black Friday"`, `"Summer Promo"`
  - Device types: `"iPhone"`, `"Android"`, `"Web"`
  - Each user generates 30–60 random events over the past 180 days.
- Events are pushed to Customer.io with `cio.track(...)` and also **saved to a local CSV** for further analysis.

### 3. Event Summary and Aggregation

- Events are loaded and aggregated by day and week.
- `pandas.resample()` is used to create a clean time series for visualization and modeling.

### 4. Trend Analysis and Spike Detection

- Daily and weekly trends are visualized using `matplotlib`.
- Spikes are identified using:
  ```python
  threshold = mean + 2 * std
  ```
- Spike days are highlighted as key anomalies in user engagement.

### 5. Forecasting and Anomaly Detection

- **ARIMA** models are trained to forecast each event type.
- Forecast vs actual plots show accuracy and fluctuation sensitivity.
- **Z-score** analysis is used to detect high/low outliers.

---

## Remarks on API Use

Customer.io's native API **does not provide access to retrieve event logs**, primarily for privacy and security reasons. Therefore:

- All analysis in this notebook is based on **simulated data** pushed through the API.
- By saving a local copy of events (`simulated_event_log.csv`), we can test analytics and time-series models on realistic engagement scenarios.

This setup mimics real-world interaction logs without violating any platform limitations or user privacy.

---

## References

- `template.API.ipynb`
- [README Guidelines](/DATA605/DATA605_Spring2025/README.md)
- `Customerio_Event_Data_utils.py`
- Notebook file: `Customerio.API.ipynb`

