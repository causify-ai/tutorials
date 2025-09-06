**Description**

CmdStanPy is a Python interface to Stan, a powerful probabilistic programming language for statistical modeling. It allows users to fit Bayesian models efficiently using Hamiltonian Monte Carlo and variational inference methods. CmdStanPy is designed for ease of use and flexibility, providing robust tools for model fitting, sampling, and diagnostics.

Technologies Used
CmdStanPy

- Provides a Pythonic interface to Stan, enabling seamless integration with Python data science workflows.
- Supports a wide range of Bayesian models, from simple linear regressions to complex hierarchical models.
- Allows for efficient sampling and inference with built-in diagnostics and visualization tools.

---

### Project 1: Predicting Housing Prices (Difficulty: 1 - Easy)

**Project Objective**  
The goal is to build a Bayesian linear regression model to predict housing prices based on various features such as location, size, and number of bedrooms. Students will optimize the model to minimize prediction error.

**Dataset Suggestions**  
Look for housing price datasets on Kaggle or government open data portals that provide real estate information.

**Tasks**  
- **Data Collection**: Gather housing data from selected sources and load it into a Pandas DataFrame.
- **Data Preprocessing**: Clean the dataset by handling missing values and encoding categorical variables.
- **Model Specification**: Define a Bayesian linear regression model using CmdStanPy.
- **Model Fitting**: Fit the model to the training data and assess convergence diagnostics.
- **Prediction**: Use the model to predict housing prices on a test set and evaluate performance using metrics like RMSE.
- **Visualization**: Create plots to visualize the relationship between features and predicted prices.

**Bonus Ideas (Optional)**  
- Compare the Bayesian model with a frequentist linear regression model.
- Extend the model to include interaction terms or polynomial features.

---

### Project 2: Customer Churn Prediction (Difficulty: 2 - Medium)

**Project Objective**  
This project aims to develop a Bayesian logistic regression model to predict customer churn for a subscription service. The objective is to identify the likelihood of a customer leaving based on their usage patterns and demographic information.

**Dataset Suggestions**  
Find customer churn datasets on Kaggle or open datasets from telecommunications or subscription-based services.

**Tasks**  
- **Data Collection**: Acquire the customer churn dataset and load it into a Pandas DataFrame.
- **Exploratory Data Analysis (EDA)**: Conduct EDA to understand the distribution of features and churn rates.
- **Model Specification**: Define a Bayesian logistic regression model using CmdStanPy.
- **Model Fitting**: Fit the model to the training data and analyze the posterior distributions of the coefficients.
- **Prediction**: Evaluate the model on a validation set by calculating precision, recall, and AUC-ROC.
- **Interpretation**: Interpret the model coefficients to understand the factors influencing churn.

**Bonus Ideas (Optional)**  
- Implement a hierarchical model to account for customer segments.
- Visualize the posterior distributions of the coefficients to communicate uncertainty.

---

### Project 3: Time Series Forecasting of Sales (Difficulty: 3 - Hard)

**Project Objective**  
The objective is to build a Bayesian state-space model to forecast future sales for a retail store. Students will optimize the model to capture trends and seasonality in the sales data.

**Dataset Suggestions**  
Look for retail sales datasets available on Kaggle or open government datasets that provide time series data.

**Tasks**  
- **Data Collection**: Gather historical sales data and preprocess it into a suitable time series format.
- **Model Specification**: Define a Bayesian state-space model to capture seasonality and trends using CmdStanPy.
- **Model Fitting**: Fit the model to the sales data and assess convergence diagnostics.
- **Forecasting**: Generate forecasts for future sales and quantify uncertainty using credible intervals.
- **Model Evaluation**: Compare the Bayesian forecasts with naive or ARIMA models using metrics like MAPE.
- **Visualization**: Create plots to visualize the observed vs. predicted sales along with uncertainty intervals.

**Bonus Ideas (Optional)**  
- Incorporate external factors (e.g., marketing campaigns) into the model.
- Experiment with different priors to see how they affect the forecasts and uncertainty.

