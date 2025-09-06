**Description**

DoWhy is a Python library designed for causal inference, allowing researchers and data scientists to estimate causal effects from observational data. It provides a structured framework to formulate causal assumptions and conduct causal analysis using graphical models. 

Technologies Used
DoWhy

- Offers a simple API for causal inference tasks including identification, estimation, and refutation of causal effects.
- Supports various causal models including linear regression, propensity score matching, and instrumental variables.
- Provides visualizations for causal graphs to help understand the relationships between variables.

---

### Project 1: Understanding the Impact of Education on Income
**Difficulty**: 1 (Easy)

**Project Objective**: Estimate the causal effect of education level on individual income, optimizing for accurate estimation of this effect using observational data.

**Dataset Suggestions**: Search for datasets related to income and education available on Kaggle or government open data portals.

**Tasks**:
- **Define Causal Graph**: Create a causal graph representing the relationship between education, income, and potential confounders (e.g., age, experience).
- **Data Preparation**: Clean and preprocess the dataset to ensure all relevant variables are included and properly formatted.
- **Causal Effect Estimation**: Use DoWhy to estimate the causal effect of education on income, applying linear regression as the estimation method.
- **Refutation Tests**: Conduct sensitivity analysis and robustness checks to validate the causal claims made.

**Bonus Ideas (Optional)**: Explore different educational attainment levels (e.g., high school, bachelor’s, master’s) and their differential impacts on income.

---

### Project 2: Evaluating Marketing Campaign Effectiveness
**Difficulty**: 2 (Medium)

**Project Objective**: Assess the causal impact of a marketing campaign on sales performance, focusing on optimizing the campaign's ROI.

**Dataset Suggestions**: Look for datasets on marketing campaigns and sales data on platforms like Kaggle or public marketing databases.

**Tasks**:
- **Causal Framework**: Develop a causal graph that includes marketing spend, sales, and other influencing factors (e.g., seasonality, competitor actions).
- **Data Cleaning and Feature Engineering**: Prepare the dataset by cleaning sales data and creating relevant features that may affect the outcome.
- **Causal Inference with DoWhy**: Estimate the causal effect of the marketing campaign using DoWhy, employing propensity score matching to control for confounding variables.
- **Impact Analysis**: Analyze the estimated impact on sales and create visualizations to illustrate the effectiveness of the campaign.

**Bonus Ideas (Optional)**: Compare the effectiveness of different marketing channels (e.g., social media vs. email marketing) and their combined effects on sales.

---

### Project 3: Analyzing the Effects of Health Interventions on Patient Outcomes
**Difficulty**: 3 (Hard)

**Project Objective**: Investigate the causal effects of a specific health intervention (e.g., a new medication) on patient recovery rates, optimizing for accurate causal inference from complex data.

**Dataset Suggestions**: Utilize health-related datasets available on Kaggle or public health databases that include patient treatment and outcome data.

**Tasks**:
- **Construct Causal Diagram**: Create a comprehensive causal graph that includes the health intervention, patient demographics, and other health-related variables.
- **Data Integration and Cleaning**: Integrate multiple data sources (e.g., patient records, treatment details) and clean the dataset for analysis.
- **Causal Effect Estimation**: Use DoWhy to estimate the causal effect of the intervention on recovery rates, applying advanced methods like instrumental variables if needed.
- **Robustness Checks**: Conduct various refutation tests to ensure the validity of the causal claims and discuss potential biases or limitations in the analysis.

**Bonus Ideas (Optional)**: Explore subgroup analyses based on patient demographics (age, gender) to see if the intervention's effectiveness varies among different populations.

