# 📈 Real-Time Bitcoin Price Forecasting with Amazon SageMaker

A fully AWS-integrated time series forecasting project that fetches real-time Bitcoin price data, streams it using Kinesis, preprocesses it with SageMaker Processing Jobs, and trains + deploys models including DeepAR, ARIMA, and Prophet — complete with autoscaling and live visualization.

---

## 🚀 Project Highlights

- 🔄 **Real-Time Data Ingestion** using CoinGecko API and **Amazon Kinesis**
- 🗃️ **Data Storage & Management** using Amazon S3
- 🧪 **Data Processing & Feature Engineering** via **SageMaker Processing Jobs**
- 📈 **Time Series Modeling** with:
  - SageMaker **DeepAR** (built-in)
  - Local **ARIMA** (statsmodels)
  - Local **Prophet** (Facebook Prophet)
- 🧠 **Model Evaluation** using MAPE and RMSE
- 🌐 **Model Deployment** as a real-time **SageMaker Endpoint**
- 📊 **Visualization** using Plotly, Matplotlib
- 📉 Optional: **Autoscaling the endpoint** for production simulation

---

## 🧱 Architecture Overview

```plaintext
             [CoinGecko API]
                    ↓
     ┌──────────────────────────────┐
     │    Real-Time Ingestion       │
     │ Python + Boto3 → Kinesis     │
     └──────────────────────────────┘
                    ↓
     ┌──────────────────────────────┐
     │     Data Lake (S3 Bucket)    │
     └──────────────────────────────┘
                    ↓
     ┌──────────────────────────────┐
     │  SageMaker Processing Job    │
     │  + Pandas, NumPy, CSV Upload │
     └──────────────────────────────┘
                    ↓
     ┌──────────────────────────────┐
     │      Model Training          │
     │ DeepAR (SageMaker Estimator) │
     └──────────────────────────────┘
                    ↓
     ┌──────────────────────────────┐
     │       Model Deployment       │
     │  SageMaker Endpoint + Test  │
     └──────────────────────────────┘
                    ↓
     ┌──────────────────────────────┐
     │      Visual Comparison       │
     │ DeepAR vs ARIMA vs Prophet  │
     └──────────────────────────────┘
