**Description**

LakeFS is an open-source data versioning tool designed to manage data lakes with Git-like capabilities. It enables data teams to easily create, manage, and collaborate on data versions, making data operations more efficient and reproducible. Key features include:
- **Data Versioning**: Track changes to datasets over time, enabling rollback and reproducibility.
- **Branching and Merging**: Create branches for data experiments, allowing for isolated changes and collaborative work.
- **Data Lake Integration**: Seamlessly integrates with existing data lakes, providing a Git-like interface for data management.
- **Data Quality and Validation**: Facilitate data validation and quality checks during versioning.

---

**Project 1: Version Control for a Customer Churn Prediction Model (Difficulty: 1)**

**Project Objective**: The goal is to create a customer churn prediction model using historical customer data. Students will utilize LakeFS to manage and version the datasets used for training and testing the model, ensuring reproducibility and ease of experimentation.

**Dataset Suggestions**: 
- **Dataset**: Telco Customer Churn Dataset available on Kaggle ([Telco Customer Churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)).
  
**Tasks**:
- Set Up LakeFS: 
    - Install LakeFS and create a repository for managing the dataset.
- Data Ingestion: 
    - Load the Telco dataset into LakeFS and create an initial version.
- Data Preprocessing: 
    - Clean and preprocess the data (handle missing values, encode categorical variables).
- Model Training: 
    - Train a logistic regression model to predict churn.
- Version Control: 
    - Use LakeFS to create branches for different preprocessing techniques and model configurations.
- Model Evaluation: 
    - Evaluate model performance using accuracy, precision, and recall metrics.

**Bonus Ideas**: 
- Experiment with different machine learning algorithms (e.g., decision trees, random forests) and compare model performance across branches.

---

**Project 2: Managing a Real Estate Price Prediction Pipeline (Difficulty: 2)**

**Project Objective**: The objective is to build a real estate price prediction model while managing the data lifecycle using LakeFS. Students will explore various features and their impacts on property prices, utilizing version control for dataset modifications.

**Dataset Suggestions**: 
- **Dataset**: Ames Housing Dataset available on Kaggle ([Ames Housing Dataset](https://www.kaggle.com/datasets/prestonv78/ames-housing-data)).
  
**Tasks**:
- Set Up LakeFS: 
    - Create a LakeFS repository and initialize a branch for the project.
- Data Exploration: 
    - Explore the Ames dataset, identifying relevant features for price prediction.
- Feature Engineering: 
    - Create new features based on existing data (e.g., total square footage).
- Model Development: 
    - Train a regression model (e.g., Random Forest Regressor) to predict house prices.
- Version Control: 
    - Use LakeFS to manage changes in feature engineering and model hyperparameters.
- Model Evaluation: 
    - Evaluate the model using RMSE and R-squared metrics.

**Bonus Ideas**: 
- Implement cross-validation techniques and compare results across different branches to optimize model performance.

---

**Project 3: Anomaly Detection in Network Traffic Data (Difficulty: 3)**

**Project Objective**: The goal is to detect anomalies in network traffic data using machine learning techniques while leveraging LakeFS for data versioning and experiment management. This project will involve handling large datasets and complex data transformations.

**Dataset Suggestions**: 
- **Dataset**: UNSW-NB15 Dataset available on Kaggle ([UNSW-NB15 Dataset](https://www.kaggle.com/datasets/mohammadami/unsw-nb15)).
  
**Tasks**:
- Set Up LakeFS: 
    - Initialize a LakeFS repository to manage the network traffic dataset.
- Data Ingestion: 
    - Load and version the UNSW-NB15 dataset in LakeFS.
- Data Preprocessing: 
    - Conduct extensive preprocessing, including normalization and feature selection.
- Anomaly Detection Model: 
    - Implement an anomaly detection algorithm (e.g., Isolation Forest or Autoencoders).
- Experiment Management: 
    - Use LakeFS to create branches for different preprocessing methods and model architectures.
- Model Evaluation: 
    - Evaluate the model using precision, recall, and F1-score metrics, focusing on true positive rates for anomalies.

**Bonus Ideas**: 
- Implement a comparative analysis of various anomaly detection techniques and visualize the results across different branches to identify the best-performing model.

