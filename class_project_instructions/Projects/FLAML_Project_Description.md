**Description**

FLAML (Fast and Lightweight AutoML) is an open-source library designed for efficient automated machine learning. It allows users to automatically select the best machine learning models and hyperparameters for their datasets while minimizing computational costs. FLAML is particularly useful for users who want to quickly prototype models without extensive machine learning expertise.

Technologies Used
FLAML

- Provides automated model selection and hyperparameter tuning.
- Optimizes for both accuracy and computational efficiency.
- Supports a variety of machine learning algorithms, including tree-based models, linear models, and deep learning.

---

### Project 1: Predicting Housing Prices
**Difficulty:** 1 (Easy)  
**Project Objective:** The goal is to predict housing prices based on various features such as location, size, and amenities. Students will optimize a regression model to achieve the lowest mean absolute error (MAE).

**Dataset Suggestions:**  
- Use the "California Housing Prices" dataset available on Kaggle: [California Housing Prices](https://www.kaggle.com/c/house-prices-advanced-regression-techniques/data).

**Tasks:**
- Data Exploration:
    - Load and visualize the dataset to understand the feature distributions and relationships.
- Data Preprocessing:
    - Handle missing values and encode categorical variables appropriately.
- Model Selection with FLAML:
    - Use FLAML to automatically select the best regression model and tune hyperparameters.
- Model Evaluation:
    - Evaluate the model using MAE and visualize the predicted vs. actual prices.
- Reporting:
    - Summarize findings and insights gained from the model performance.

---

### Project 2: Customer Churn Prediction
**Difficulty:** 2 (Medium)  
**Project Objective:** The aim is to predict customer churn for a subscription-based service. Students will optimize a classification model to improve accuracy and recall, focusing on identifying customers likely to leave.

**Dataset Suggestions:**  
- Use the "Telco Customer Churn" dataset available on Kaggle: [Telco Customer Churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn).

**Tasks:**
- Data Exploration:
    - Analyze customer demographics and churn patterns using visualizations.
- Feature Engineering:
    - Create new features based on existing data, such as tenure groups or service combinations.
- Model Selection with FLAML:
    - Implement FLAML to select and tune classification algorithms (e.g., Random Forest, Logistic Regression) for churn prediction.
- Model Evaluation:
    - Assess the model using accuracy, precision, recall, and F1-score.
- Insights and Recommendations:
    - Provide actionable insights based on model predictions to improve customer retention strategies.

---

### Project 3: Stock Price Movement Prediction
**Difficulty:** 3 (Hard)  
**Project Objective:** The objective is to predict the movement of stock prices (up or down) based on historical price data and technical indicators. Students will optimize a classification model to achieve high accuracy while dealing with noisy financial data.

**Dataset Suggestions:**  
- Use the "S&P 500 Stock Data" dataset from Yahoo Finance via the yfinance library, which allows fetching historical stock data directly.

**Tasks:**
- Data Collection:
    - Use the yfinance library to download historical stock prices and calculate technical indicators (e.g., moving averages, RSI).
- Data Preprocessing:
    - Clean the dataset, handle missing values, and create a target variable indicating upward or downward price movement.
- Model Selection with FLAML:
    - Leverage FLAML to automatically select and tune models suitable for classification tasks on time-series data.
- Model Evaluation:
    - Evaluate the model using accuracy, confusion matrix, and ROC-AUC score.
- Advanced Analysis:
    - Conduct a sensitivity analysis to understand how different features impact stock price movement predictions.

**Bonus Ideas (Optional):**
- For Project 1, compare FLAML's results with manual hyperparameter tuning using GridSearchCV.
- For Project 2, implement a cost-sensitive model to account for the costs associated with false negatives (missed churn).
- For Project 3, explore ensemble methods or stacking models to improve prediction robustness.

