**Description**

CausalNex is a Python library designed for causal inference and causal modeling, enabling data scientists to understand the relationships between variables and their effects on outcomes. It allows for the construction of causal graphs, estimation of causal effects, and testing of causal assumptions. 

Technologies Used
CausalNex

- Facilitates the creation and visualization of Bayesian networks for causal inference.
- Supports causal effect estimation through interventions and counterfactual reasoning.
- Offers tools for model learning from data, including structure learning and parameter estimation.

---

### Project 1: Understanding Factors Affecting Student Performance

**Difficulty**: 1 (Easy)

**Project Objective**: The goal of this project is to identify and analyze the causal relationships between various factors (e.g., study time, attendance, socioeconomic status) and student performance in exams, optimizing for the prediction of student grades.

**Dataset Suggestions**: 
- Use the "Student Performance Data Set" available on Kaggle: [Student Performance Data](https://www.kaggle.com/datasets/uciml/student-alcohol-consumption).

**Tasks**:
- Data Preparation:
  - Load and preprocess the dataset, handling missing values and encoding categorical variables.
  
- Construct Causal Graph:
  - Use CausalNex to create a causal graph that represents the relationships between identified factors and student performance.

- Estimate Causal Effects:
  - Apply CausalNex to estimate the causal effects of different factors on student grades.

- Visualization:
  - Visualize the causal graph and the estimated effects to communicate findings effectively.

---

### Project 2: Analyzing the Impact of Marketing Campaigns on Sales

**Difficulty**: 2 (Medium)

**Project Objective**: This project aims to analyze how different marketing strategies (e.g., social media, email marketing, discounts) causally influence sales figures, optimizing for the identification of the most effective marketing channels.

**Dataset Suggestions**: 
- Utilize the "Marketing Campaigns Dataset" available on Kaggle: [Marketing Campaign Data](https://www.kaggle.com/datasets/rohanrao96/marketing-campaign).

**Tasks**:
- Data Cleaning and Exploration:
  - Clean the dataset and explore the relationships between marketing strategies and sales.

- Build Causal Model:
  - Construct a causal model using CausalNex to represent the marketing strategies and their effects on sales.

- Interventional Analysis:
  - Perform interventional analysis to simulate the effect of increasing various marketing efforts on sales.

- Sensitivity Analysis:
  - Conduct sensitivity analysis to understand how robust the causal relationships are to changes in assumptions.

---

### Project 3: Understanding the Drivers of Health Outcomes in Patients

**Difficulty**: 3 (Hard)

**Project Objective**: The goal is to uncover the complex causal relationships between various health indicators (e.g., lifestyle choices, genetic factors, medication adherence) and health outcomes (e.g., disease progression, recovery rates) in patients, optimizing for predictive accuracy in health outcomes.

**Dataset Suggestions**: 
- Use the "Framingham Heart Study Dataset" available on Kaggle: [Framingham Heart Study](https://www.kaggle.com/datasets/amanbansal/framingham-heart-study-dataset).

**Tasks**:
- Data Integration and Cleaning:
  - Integrate multiple sources of health data and perform thorough cleaning and preprocessing.

- Causal Graph Construction:
  - Develop a detailed causal graph using CausalNex to represent the complex relationships among health indicators and outcomes.

- Causal Effect Estimation:
  - Estimate causal effects using CausalNex, focusing on how lifestyle changes might impact health outcomes.

- Counterfactual Analysis:
  - Conduct counterfactual analysis to predict health outcomes under different scenarios of lifestyle changes.

- Model Validation:
  - Validate the causal model using holdout datasets and compare with traditional predictive models to assess improvements in understanding health outcomes.

**Bonus Ideas (Optional)**:
- Extend the analysis by incorporating machine learning models for predictive insights.
- Compare causal estimates with traditional regression analyses for deeper insights into model performance.
- Investigate the role of external factors (e.g., socioeconomic status) on health outcomes and their interactions with health indicators.

