**Description**

In this project, students will utilize sktime, a Python library specifically designed for time series analysis, to build models for forecasting and analyzing temporal data. sktime provides a unified interface for various time series tasks, including classification, regression, and clustering, making it versatile for different applications. 

Technologies Used
sktime

- Supports a wide range of time series algorithms for classification, regression, and clustering.
- Provides tools for preprocessing, feature extraction, and model evaluation tailored for time series data.
- Facilitates the integration of machine learning libraries like scikit-learn for enhanced modeling capabilities.

---

### Project 1: Sales Forecasting for a Retail Store
**Difficulty**: 1 (Easy)  
**Project Objective**: The goal is to forecast monthly sales for a retail store using historical sales data to optimize inventory management.

**Dataset Suggestions**: Use the "Retail Sales Forecasting" dataset available on Kaggle. This dataset contains historical sales data for various products in a retail environment.

**Tasks**:
- **Data Preprocessing**: Load the dataset and clean any missing or erroneous values.
- **Time Series Decomposition**: Decompose the time series into trend, seasonality, and residuals using sktime functions.
- **Model Selection**: Choose and implement a suitable forecasting model (e.g., ARIMA, Exponential Smoothing).
- **Model Evaluation**: Evaluate the model's performance using metrics like Mean Absolute Error (MAE) and visualize the forecast against actual sales.
- **Visualization**: Create plots to visualize sales trends, forecasts, and evaluation metrics using Matplotlib.

---

### Project 2: Anomaly Detection in Server Load Data
**Difficulty**: 2 (Medium)  
**Project Objective**: The objective is to detect anomalies in server load data to identify potential issues in system performance.

**Dataset Suggestions**: Use the "Yahoo Webscope S5" dataset available on Kaggle, which contains time series data of server load with labeled anomalies.

**Tasks**:
- **Data Ingestion**: Load the server load dataset and preprocess it to handle missing values and outliers.
- **Feature Engineering**: Extract relevant features from the time series data, such as rolling means and standard deviations.
- **Anomaly Detection**: Implement anomaly detection algorithms (e.g., Isolation Forest, Seasonal Decomposition) using sktime.
- **Evaluation**: Assess the effectiveness of the anomaly detection by comparing detected anomalies with the ground truth labels.
- **Visualization**: Plot the original server load data with detected anomalies highlighted for better interpretation.

---

### Project 3: Multi-step Time Series Forecasting of Air Quality
**Difficulty**: 3 (Hard)  
**Project Objective**: The goal is to predict future air quality index (AQI) values based on historical data to inform public health decisions.

**Dataset Suggestions**: Use the "Air Quality Data Set" from the UCI Machine Learning Repository, which contains hourly measurements of various pollutants.

**Tasks**:
- **Data Preparation**: Load the AQI dataset and preprocess it by handling missing values and normalizing the data.
- **Feature Extraction**: Use sktime's tools to create lag features and rolling statistics to enhance the predictive power of the model.
- **Model Development**: Implement a multi-step forecasting approach using advanced models such as Long Short-Term Memory (LSTM) networks or Prophet.
- **Hyperparameter Tuning**: Optimize model parameters to improve forecast accuracy using cross-validation techniques.
- **Performance Evaluation**: Assess the model's performance using metrics like RMSE and visualize the predicted vs actual AQI values over time.

**Bonus Ideas (Optional)**: 
- Explore the impact of weather data on AQI predictions by integrating additional datasets.
- Compare the performance of different forecasting models to identify the best approach for multi-step forecasting.
- Implement an interactive dashboard using Plotly Dash to visualize real-time AQI forecasts and trends.

