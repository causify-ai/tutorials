**Description**

In this project, students will utilize bnlearn, a Python library for Bayesian network learning and inference, to model and analyze probabilistic relationships among variables. This tool allows for both structure learning from data and inference queries, providing insights into dependencies and causal relationships. Students will explore how to build Bayesian networks, perform inference, and visualize the learned structures.

Technologies Used
bnlearn

- Facilitates learning of Bayesian networks from data.
- Supports structure learning and parameter estimation.
- Enables probabilistic inference and querying of the network.
- Provides visualization capabilities for the learned structures.

---

### Project 1: Disease Prediction using Bayesian Networks (Difficulty: 1)

**Project Objective:**
Develop a Bayesian network to predict the likelihood of a disease based on various symptoms and risk factors, optimizing for accuracy in predictions.

**Dataset Suggestions:**
Find datasets related to health and disease symptoms on Kaggle or open government health databases.

**Tasks:**
- **Data Collection:**
  - Gather a dataset containing symptoms, demographics, and disease outcomes.
  
- **Data Preprocessing:**
  - Clean the dataset, handle missing values, and encode categorical variables.
  
- **Bayesian Network Structure Learning:**
  - Use bnlearn to learn the structure of the Bayesian network from the data.
  
- **Parameter Estimation:**
  - Estimate the conditional probability tables for the variables in the network.
  
- **Inference:**
  - Perform inference on the network to predict the disease given specific symptoms.
  
- **Evaluation:**
  - Validate the model's predictions using cross-validation and assess accuracy.

---

### Project 2: Customer Churn Analysis (Difficulty: 2)

**Project Objective:**
Create a Bayesian network to analyze customer churn in a subscription-based service, optimizing for understanding the key factors influencing customer retention.

**Dataset Suggestions:**
Utilize datasets from Kaggle related to customer behavior and churn analysis.

**Tasks:**
- **Data Acquisition:**
  - Obtain a dataset that includes customer demographics, service usage, and churn status.
  
- **Exploratory Data Analysis:**
  - Conduct EDA to understand relationships and distributions among variables.
  
- **Bayesian Network Construction:**
  - Use bnlearn to learn the structure of the network based on the dataset.
  
- **Inference and Analysis:**
  - Perform inference to identify the likelihood of churn given different customer attributes.
  
- **Sensitivity Analysis:**
  - Analyze how changes in certain features affect churn probability.
  
- **Visualization:**
  - Visualize the Bayesian network and the relationships among variables.

---

### Project 3: Predicting Academic Performance using Bayesian Networks (Difficulty: 3)

**Project Objective:**
Build a complex Bayesian network to predict students’ academic performance based on various factors such as socio-economic status, study habits, and attendance, optimizing for predictive accuracy and interpretability.

**Dataset Suggestions:**
Access educational datasets from open repositories or Kaggle that include student performance metrics and associated factors.

**Tasks:**
- **Dataset Exploration:**
  - Identify and gather a dataset with comprehensive features related to student performance.
  
- **Data Preprocessing:**
  - Clean the data, manage missing values, and encode categorical variables appropriately.
  
- **Complex Structure Learning:**
  - Use bnlearn to learn a complex structure that captures intricate dependencies among factors affecting performance.
  
- **Parameter Estimation:**
  - Estimate parameters for the Bayesian network, ensuring robustness in the model.
  
- **Inference and Scenario Analysis:**
  - Use the model to predict performance under various hypothetical scenarios (e.g., changes in study habits).
  
- **Model Evaluation:**
  - Evaluate the model's performance using appropriate metrics and compare with basic predictive models (e.g., regression).

**Bonus Ideas (Optional):**
- Implement a feature selection method to identify the most influential factors in the network.
- Explore the impact of introducing new variables (e.g., extracurricular activities) on the model's predictions.
- Conduct a longitudinal study by applying the model to different academic years to assess stability and changes in relationships.

