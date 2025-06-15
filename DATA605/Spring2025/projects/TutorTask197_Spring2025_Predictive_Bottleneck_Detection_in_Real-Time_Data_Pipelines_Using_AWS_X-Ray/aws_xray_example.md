#  Bitcoin AWS X-RAY Pipeline Example Explanation

This document explains the purpose, flow, and logic behind the `aws_xray_example.ipynb` notebook, which demonstrates the real-time latency monitoring pipeline using AWS services and time-series forecasting.

---

##  Objective

The goal of the notebook is to simulate an end-to-end walkthrough that:

* Ingests and processes real Bitcoin data
* Uses AWS X-Ray to trace function latency
* Computes performance metrics
* Applies forecasting with Prophet
* Detects anomalies
* Visualizes predictions and price trends

---

## Step-by-Step Breakdown

### 1. **Load Trace Data**

* `load_trace_data()` dynamically pulls the latest annotated trace segments from AWS X-Ray.
* Duplicates are removed.
* `timestamp` and `hour_str` columns are parsed as datetime objects to enable time-based aggregation and analysis.

### 2. **Hourly Metrics**

* Aggregates metrics like average latency, request counts, data volume, and error rates on an hourly basis.
* Adds rolling averages for smooth trend observation.

### 3. **Forecast Latency (Hourly)**

* Uses Prophet to predict future latency over the next 24 hours.
* Displays prediction and confidence interval.

### 4. **Detect Anomalies**

* Any predicted latency above a defined threshold (e.g., 150ms) is flagged as an anomaly.

### 5. **Daily Aggregation & Forecast**

* Similar to hourly, but aggregated daily.
* Useful for longer-term system trends.

### 6. **Price Over Time**

* Bitcoin price from the trace annotations is plotted over time.
* Gives context to how price behavior relates to system performance.

---

## How to Run This in Docker

To run this notebook within the Docker environment:

1. **Make sure `main.py` and this notebook are part of `/app`**
2. Ensure Dockerfile includes:

```dockerfile
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
```

3. Modify `run.sh` to:

```bash
#!/bin/bash
jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root
```

4. Build and run:

```bash
docker build -t aws-xray-example .
docker run -p 8888:8888 aws-xray-example
```

5. Open Jupyter in the browser using the link from terminal logs.

---

## Summary

This notebook serves as a standalone demonstration of the entire AWS-powered, real-time, latency-forecasting pipeline. It includes all components: ingestion, storage, monitoring, forecasting, and visualization.
