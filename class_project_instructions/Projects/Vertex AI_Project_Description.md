**Description**

In this project, students will utilize Vertex AI, a unified machine learning platform by Google Cloud, to build and deploy machine learning models efficiently. Vertex AI provides tools for data preparation, model training, and deployment, making it easier to manage the entire ML lifecycle. 

Technologies Used
Vertex AI

- Offers a fully managed environment for training and deploying ML models.
- Integrates seamlessly with Google Cloud services for data storage and processing.
- Provides AutoML capabilities for automated model training and hyperparameter tuning.
- Supports various ML frameworks, including TensorFlow, PyTorch, and scikit-learn.

---

**Project 1: Predicting Housing Prices**  
**Difficulty**: 1 (Easy)  
**Project Objective**: The goal is to predict housing prices based on various features such as location, size, and number of bedrooms. The project will optimize the model for accuracy in price predictions.

**Dataset Suggestions**: Use the "California Housing Prices" dataset available on Kaggle: [California Housing Prices](https://www.kaggle.com/c/house-prices-advanced-regression-techniques/data).

**Tasks**:
- Data Ingestion:
  - Load the dataset into Google Cloud Storage.
  - Use Vertex AI to create a dataset resource for model training.

- Data Preprocessing:
  - Clean the data, handle missing values, and perform feature scaling.
  - Split the data into training and testing sets.

- Model Training:
  - Use Vertex AI AutoML to train a regression model on the processed dataset.
  - Evaluate the model's performance using metrics like RMSE.

- Model Deployment:
  - Deploy the trained model to Vertex AI for predictions.
  - Create a simple web interface to input features and retrieve predicted prices.

---

**Project 2: Customer Churn Prediction**  
**Difficulty**: 2 (Medium)  
**Project Objective**: The aim is to predict customer churn for a subscription-based service, optimizing the model for recall to identify customers likely to leave.

**Dataset Suggestions**: Use the "Telco Customer Churn" dataset available on Kaggle: [Telco Customer Churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn).

**Tasks**:
- Data Ingestion and Exploration:
  - Load the dataset into Google Cloud Storage and create a dataset resource in Vertex AI.
  - Perform exploratory data analysis (EDA) to understand feature distributions and correlations.

- Feature Engineering:
  - Create new features based on existing data (e.g., tenure groups, total charges).
  - Encode categorical variables and scale numerical features.

- Model Training:
  - Train a classification model (e.g., decision tree, random forest) using Vertex AI.
  - Optimize the model for recall using hyperparameter tuning.

- Model Evaluation:
  - Evaluate the model using confusion matrix and ROC-AUC score.
  - Analyze feature importance to understand key drivers of churn.

- Deployment:
  - Deploy the model to Vertex AI and create a dashboard for real-time predictions.

---

**Project 3: Real-time Sentiment Analysis on Tweets**  
**Difficulty**: 3 (Hard)  
**Project Objective**: The goal is to perform real-time sentiment analysis on tweets related to a trending topic, optimizing the model for accuracy and response time.

**Dataset Suggestions**: Use the "Sentiment140" dataset available on Kaggle: [Sentiment140](https://www.kaggle.com/datasets/kazanova/sentiment140).

**Tasks**:
- Data Ingestion:
  - Load the dataset into Google Cloud Storage and create a dataset resource in Vertex AI.
  - Preprocess the text data (tokenization, stopword removal).

- Model Selection and Training:
  - Fine-tune a pre-trained transformer model (e.g., BERT) using Vertex AI.
  - Implement transfer learning techniques to adapt the model for sentiment classification.

- Real-time Data Streaming:
  - Use Twitter API to stream tweets in real-time related to a specific hashtag.
  - Implement a pipeline to preprocess incoming tweets and feed them to the model for predictions.

- Model Evaluation:
  - Assess the model's performance using accuracy and F1-score on a validation set.
  - Analyze misclassifications to improve the model.

- Visualization and Reporting:
  - Create a dashboard to visualize sentiment trends over time.
  - Provide insights on how sentiment correlates with real-world events related to the trending topic.

**Bonus Ideas (Optional)**: 
- For Project 1, consider implementing a feature importance analysis to better understand which features significantly impact housing prices.
- For Project 2, explore using ensemble methods to improve model performance and compare against baseline models.
- For Project 3, extend the dashboard to include geographical sentiment mapping using the location data from tweets.

