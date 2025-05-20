Real-Time Bitcoin Price Forecasting – Code Walkthrough
This document provides a detailed walkthrough of the project code in ak605final.ipynb. The notebook implements a real-time Bitcoin forecasting pipeline using AWS SageMaker, Kinesis, S3, and three time series models: DeepAR, ARIMA, and Prophet.

**🗂️ 1. Configuration & Setup**
python
Copy
Edit
REGION = sagemaker.Session().boto_region_name
SESSION = sagemaker.Session()
ROLE = sagemaker.get_execution_role()
BUCKET = 'your-s3-bucket'
PREDICTION_LENGTH = 12
KINESIS_STREAM = "btc-price-stream"
Purpose: Sets up AWS region, IAM role, S3 bucket name, prediction horizon, and optional Kinesis stream.

**🌐 2. Data Ingestion**
python
Copy
Edit
def fetch_btc_data(days=30):
    ...
df = fetch_btc_data(days=30)
df.to_csv("btc_raw.csv")
Source: CoinGecko API

Format: Timestamps and prices (hourly granularity)

Stored as: btc_raw.csv

**🔁 3. Kinesis Simulation**
python
Copy
Edit
send_btc_to_kinesis(df, stream_name)
Simulates real-time streaming by sending BTC price data to a Kinesis stream.

**☁️ 4. Upload Raw Data to S3**
python
Copy
Edit
s3.upload_file("btc_raw.csv", BUCKET, f"{input_prefix}/btc_raw.csv")
Uploads the raw CSV to S3 for SageMaker Processing to access.

**⚙️ 5. Data Preprocessing with SageMaker Processing Job**
python
Copy
Edit
ScriptProcessor(...).run(...)
Uses a custom Python script to:

Parse timestamps

Add rolling mean & volatility

Compute returns and z-scores

Extract time-based features (hour, day_of_week)

Save cleaned CSV to S3 as btc_cleaned.csv

**📊 6. Visualization: EDA & Insights**
➤ Rolling Mean + Volatility Plot
python
Copy
Edit
go.Scatter(... name="12h Rolling Mean")
go.Scatter(... name="Volatility Upper / Lower")
➤ Returns Histogram
python
Copy
Edit
plt.hist(... title="Distribution of Hourly BTC Returns")
➤ Time Series Decomposition
python
Copy
Edit
seasonal_decompose(df_cleaned['price'], model='additive')
Shows trend, seasonality, and residuals

**📁 7. DeepAR: Training on SageMaker**
python
Copy
Edit
deep_ar = Estimator(...)
deep_ar.set_hyperparameters(...)
deep_ar.fit(...)
Uses SageMaker’s built-in DeepAR container

Inputs: Cleaned data in JSON format

Hyperparameters include:

epochs, context_length, num_cells, learning_rate, etc.

**🚀 8. Deployment & Autoscaling**
python
Copy
Edit
predictor = deep_ar.deploy(...)
autoscale.register_scalable_target(...)
autoscale.put_scaling_policy(...)
Deploys the DeepAR model as a SageMaker endpoint

Enables autoscaling for production-like simulation

**🔮 9. Prediction & Forecast Extraction**
python
Copy
Edit
predictor.predict(input_data)
Extracts mean, P10, and P90 predictions

Generates a future time index for plotting

**📈 10. DeepAR Forecast Visualization**
python
Copy
Edit
go.Figure([
    "Historical",
    "DeepAR Mean Forecast",
    "Prediction Bounds"
])
Clearly shows model forecast with confidence intervals

**📉 11. ARIMA Forecast (Local)**
python
Copy
Edit
model_arima = ARIMA(...).fit()
forecast_arima = model_arima.forecast()
Classic statistical baseline

Evaluation: RMSE, MAPE

**🔁 12. Prophet Forecast (Local)**
python
Copy
Edit
prophet = Prophet(...)
forecast = prophet.predict(...)
Models trend + seasonality

Evaluation: RMSE, MAPE

**🧪 13. Evaluation Metrics**
python
Copy
Edit
mean_squared_error(...), mean_absolute_percentage_error(...)
Compares model predictions against actual BTC prices

Shows performance of each model (ARIMA, Prophet, DeepAR)

**📊 14. Final Comparison Plot**
python
Copy
Edit
go.Figure([
    "Historical",
    "ARIMA Forecast",
    "Prophet Forecast",
    "DeepAR Forecast"
])
Side-by-side visual comparison of all 3 models
