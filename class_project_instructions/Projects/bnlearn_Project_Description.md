**Description**

In this project, students will utilize bnlearn, a Python library designed for learning and inference in Bayesian networks. This tool allows for the construction of probabilistic graphical models that represent a set of variables and their conditional dependencies. Key features include:

- Structure learning from data using various algorithms (e.g., hill climbing, constraint-based).
- Parameter learning to estimate the conditional probability distributions.
- Inference capabilities to compute posterior probabilities and make predictions based on evidence.

---

### Project 1: Predicting Student Performance (Difficulty: 1)

**Project Objective**:  
The goal is to create a Bayesian network to predict student performance based on various factors such as study habits, attendance, and socio-economic status. The model will help in identifying key factors influencing academic success.

**Dataset Suggestions**:  
- Use the "Student Performance Dataset" available on Kaggle: [Student Performance Data](https://www.kaggle.com/datasets/uciml/student-alcohol-consumption).

**Tasks**:
- Data Preprocessing:
    - Load the dataset and clean the data by handling missing values and encoding categorical variables.
  
- Construct the Bayesian Network:
    - Use bnlearn to define the structure of the network based on domain knowledge or initial analysis.

- Parameter Learning:
    - Estimate the conditional probability distributions for the network using the dataset.

- Inference:
    - Perform inference to predict the likelihood of students achieving a certain grade based on their attributes.

- Evaluation:
    - Assess the model's predictive accuracy using appropriate metrics like accuracy and confusion matrix.

---

### Project 2: Diagnosing Heart Disease (Difficulty: 2)

**Project Objective**:  
The objective is to develop a Bayesian network model that can diagnose heart disease based on various medical indicators and patient history, optimizing for sensitivity and specificity in predictions.

**Dataset Suggestions**:  
- Utilize the "Heart Disease UCI" dataset available on Kaggle: [Heart Disease Dataset](https://www.kaggle.com/datasets/ronitf/heart-disease-uci).

**Tasks**:
- Data Exploration:
    - Conduct exploratory data analysis (EDA) to understand the relationships and distributions of variables.

- Bayesian Network Structure Learning:
    - Apply bnlearn to learn the structure of the Bayesian network from the data using constraint-based methods.

- Parameter Estimation:
    - Use the dataset to estimate the conditional probabilities associated with the network.

- Model Inference:
    - Implement inference techniques to predict the probability of heart disease given patient symptoms and history.

- Model Evaluation:
    - Evaluate the model using ROC curves and calculate AUC to assess diagnostic performance.

---

### Project 3: Predicting Customer Churn (Difficulty: 3)

**Project Objective**:  
The goal is to create a complex Bayesian network that predicts customer churn in a subscription-based service, optimizing for actionable insights into customer retention strategies.

**Dataset Suggestions**:  
- Leverage the "Telco Customer Churn" dataset available on Kaggle: [Telco Customer Churn Dataset](https://www.kaggle.com/datasets/blastchar/telco-customer-churn).

**Tasks**:
- Comprehensive Data Preprocessing:
    - Clean and preprocess the dataset, including feature engineering to create meaningful variables.

- Advanced Structure Learning:
    - Use bnlearn to learn the structure of the network with a focus on capturing complex relationships among variables.

- Parameter Learning:
    - Estimate the conditional probabilities using Bayesian methods to fit the model.

- Inference and Scenario Analysis:
    - Perform inference to predict churn probability under various scenarios (e.g., changes in service usage or customer support interactions).

- Sensitivity Analysis:
    - Conduct sensitivity analysis to determine how changes in input variables affect churn predictions.

**Bonus Ideas (Optional)**:
- Implement a dynamic Bayesian network to model churn over time.
- Compare the performance of the Bayesian network with traditional classification models (e.g., logistic regression, random forest).
- Explore the impact of marketing interventions on churn rates through scenario simulations.

