**Description**

Pyro is a flexible, scalable deep probabilistic programming library built on PyTorch, designed for Bayesian modeling and inference. It allows users to define probabilistic models and perform inference using modern techniques like variational inference and Markov Chain Monte Carlo (MCMC). 

Technologies Used
Pyro

- Enables probabilistic modeling with a focus on Bayesian methods.
- Supports both variational inference and MCMC for flexible inference options.
- Integrates seamlessly with PyTorch for deep learning capabilities.

---

### Project 1: Predicting Housing Prices with Bayesian Linear Regression (Difficulty: 1)

**Project Objective**  
The goal of this project is to build a Bayesian linear regression model to predict housing prices based on various features such as location, square footage, and number of bedrooms. Students will focus on understanding the uncertainty in predictions.

**Dataset Suggestions**  
- **Dataset**: "Ames Housing Dataset"  
- **Source**: Available on Kaggle [Ames Housing Dataset](https://www.kaggle.com/datasets/prestonvong/austin-housing-data)

**Tasks**  
- Data Preprocessing:
  - Clean the dataset by handling missing values and encoding categorical variables.
  
- Model Definition:
  - Define a Bayesian linear regression model using Pyro.

- Inference:
  - Perform variational inference to estimate the posterior distributions of model parameters.

- Prediction:
  - Use the model to predict house prices and quantify uncertainty in predictions.

- Evaluation:
  - Compare the Bayesian model's predictions against a standard linear regression model using metrics like RMSE and MAE.

---

### Project 2: Topic Modeling with Bayesian Hierarchical Models (Difficulty: 2)

**Project Objective**  
This project aims to implement a Bayesian hierarchical model for topic modeling on a collection of news articles, allowing students to discover latent topics and understand the uncertainty involved in topic assignments.

**Dataset Suggestions**  
- **Dataset**: "20 Newsgroups Dataset"  
- **Source**: Available on Hugging Face [20 Newsgroups Dataset](https://huggingface.co/datasets/20newsgroups)

**Tasks**  
- Data Preparation:
  - Preprocess the text data by removing stop words, stemming, and vectorizing the text.

- Model Specification:
  - Define a Bayesian hierarchical model for topic modeling using Pyro.

- Inference:
  - Utilize MCMC methods to sample from the posterior distribution of topics.

- Topic Extraction:
  - Analyze the output to identify and interpret the discovered topics.

- Visualization:
  - Create visualizations (e.g., word clouds) to represent the most significant words in each topic.

---

### Project 3: Anomaly Detection in Time-Series Data (Difficulty: 3)

**Project Objective**  
The objective is to implement a Bayesian approach to detect anomalies in time-series data, such as stock prices, by modeling the underlying data generation process and identifying deviations from expected behavior.

**Dataset Suggestions**  
- **Dataset**: "Yahoo Finance Stock Prices"  
- **Source**: Use the Yahoo Finance API (free and active) to gather historical stock price data for a selected company.

**Tasks**  
- Data Collection:
  - Use the Yahoo Finance API to fetch historical stock price data.

- Data Preprocessing:
  - Clean and preprocess the time-series data, ensuring proper formatting and handling missing values.

- Model Development:
  - Define a Bayesian state space model in Pyro to capture the underlying trends and seasonality.

- Anomaly Detection:
  - Use posterior predictive checks to identify anomalies based on deviations from the expected distribution.

- Evaluation:
  - Validate the detected anomalies against known significant events in the stock's history and assess model performance.

**Bonus Ideas (Optional)**  
- Implement a comparative study with traditional anomaly detection techniques (e.g., Z-score, Isolation Forest).
- Extend the model to include external factors (e.g., economic indicators) and assess their impact on anomaly detection.

