**Description**

In this project, students will utilize TensorFlow Probability, a library for probabilistic reasoning and statistical analysis, to build and evaluate probabilistic models. TensorFlow Probability integrates seamlessly with TensorFlow, enabling students to leverage its powerful tools for Bayesian modeling, probabilistic programming, and statistical inference.

Technologies Used
TensorFlow Probability

- Provides building blocks for probabilistic models, including distributions and bijectors.
- Supports variational inference and MCMC methods for Bayesian analysis.
- Facilitates the integration of probabilistic models with deep learning frameworks.

---

### Project 1: Predicting Housing Prices Using Bayesian Regression
**Difficulty**: 1 (Easy)

**Project Objective**: 
Build a Bayesian regression model to predict housing prices based on various features such as size, location, and number of bedrooms. The goal is to optimize the model's predictive accuracy while quantifying uncertainty in the predictions.

**Dataset Suggestions**: 
- Use the "Housing Prices - Advanced Regression Techniques" dataset from Kaggle: [Housing Prices Dataset](https://www.kaggle.com/c/house-prices-advanced-regression-techniques/data).

**Tasks**:
- Data Preprocessing:
  - Clean the dataset by handling missing values and encoding categorical features.
  
- Exploratory Data Analysis:
  - Visualize relationships between features and target variable using scatter plots and correlation matrices.
  
- Bayesian Model Development:
  - Construct a Bayesian regression model using TensorFlow Probability, specifying prior distributions for the parameters.
  
- Model Training:
  - Fit the model to the training data and perform posterior inference using variational inference.
  
- Predictions and Evaluation:
  - Generate predictions on the test set and evaluate the model using metrics such as RMSE and R-squared.
  
- Uncertainty Quantification:
  - Analyze the uncertainty of predictions by exploring credible intervals.

---

### Project 2: Time Series Forecasting with Probabilistic Models
**Difficulty**: 2 (Medium)

**Project Objective**: 
Develop a probabilistic time series forecasting model to predict future values of a stock based on historical prices. The aim is to optimize the model's accuracy and provide uncertainty estimates for the predictions.

**Dataset Suggestions**: 
- Use the "S&P 500 Stock Data" from Yahoo Finance API (free and active): [Yahoo Finance API](https://finance.yahoo.com/quote/%5EGSPC/history?p=%5EGSPC).

**Tasks**:
- Data Collection:
  - Fetch historical stock prices using the Yahoo Finance API and preprocess the data for time series analysis.
  
- Exploratory Data Analysis:
  - Analyze the time series data for trends, seasonality, and stationarity using visualizations and statistical tests.
  
- Model Construction:
  - Build a probabilistic time series model (e.g., Gaussian Process or ARIMA) using TensorFlow Probability.
  
- Parameter Estimation:
  - Use MCMC methods to estimate the parameters of the model and assess model fit.
  
- Forecasting:
  - Generate forecasts for future stock prices and visualize the predictions along with uncertainty bands.
  
- Model Evaluation:
  - Evaluate the forecasting performance using metrics such as MAE and MAPE.

---

### Project 3: Anomaly Detection in Network Traffic Data
**Difficulty**: 3 (Hard)

**Project Objective**: 
Create a probabilistic model to detect anomalies in network traffic data. The goal is to identify unusual patterns that could indicate potential security threats, optimizing the detection rate while minimizing false positives.

**Dataset Suggestions**: 
- Use the "CICIDS 2017" dataset available on Kaggle: [CICIDS 2017 Dataset](https://www.kaggle.com/datasets/abhinavpoudel/cicids-2017).

**Tasks**:
- Data Preprocessing:
  - Clean and preprocess the dataset, including feature selection and normalization.
  
- Exploratory Data Analysis:
  - Conduct a thorough analysis of traffic patterns, visualizing distributions and correlations among features.
  
- Model Development:
  - Implement a probabilistic anomaly detection model (e.g., Variational Autoencoder) using TensorFlow Probability.
  
- Training and Evaluation:
  - Train the model on normal traffic data and evaluate its ability to detect anomalies using precision, recall, and F1-score.
  
- Anomaly Scoring:
  - Develop a scoring mechanism to quantify the severity of detected anomalies based on the model's output.
  
- Visualization:
  - Visualize the anomalies detected over time and analyze their implications for network security.

**Bonus Ideas**:
- Experiment with different prior distributions and model architectures to improve anomaly detection performance.
- Compare the probabilistic model's performance with traditional machine learning models (e.g., Random Forest, SVM) for anomaly detection.
- Implement real-time anomaly detection using streaming data from a public API.

