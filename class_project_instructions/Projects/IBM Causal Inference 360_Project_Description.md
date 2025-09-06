**Description**

IBM Causal Inference 360 is an open-source toolkit designed for causal analysis, enabling data scientists to understand and quantify the causal relationships in their datasets. It provides a suite of algorithms to identify and estimate causal effects, allowing users to conduct robust causal inference in various domains.

Technologies Used
IBM Causal Inference 360

- Offers a variety of causal inference algorithms including propensity score matching, regression discontinuity, and instrumental variable methods.
- Supports both observational and experimental data for causal analysis.
- Facilitates the evaluation of treatment effects and causal relationships through comprehensive model diagnostics and visualizations.

---

**Project 1: Evaluating the Impact of Online Learning on Student Performance**  
**Difficulty**: 1 (Easy)  
**Project Objective**: To estimate the causal effect of online learning on student performance in mathematics by analyzing historical academic data.

**Dataset Suggestions**: Look for public datasets from educational institutions or government portals that track student performance metrics over time.

**Tasks**:
- Data Collection:
    - Gather student performance data before and after the implementation of online learning.
    - Clean and preprocess the dataset to ensure its suitability for analysis.
  
- Propensity Score Matching:
    - Apply propensity score matching to create balanced groups of students (those who experienced online learning vs. those who did not).
  
- Causal Effect Estimation:
    - Use IBM Causal Inference 360 to estimate the treatment effect of online learning on student performance.
  
- Model Diagnostics:
    - Evaluate the robustness of the causal estimates through diagnostic checks and visualizations.
  
- Reporting Results:
    - Present findings in a clear report, including visualizations of the causal impact.

**Bonus Ideas**: Extend the analysis by exploring different subjects, or compare the impact of online learning across different demographic groups.

---

**Project 2: Assessing the Effectiveness of Marketing Campaigns on Sales**  
**Difficulty**: 2 (Medium)  
**Project Objective**: To analyze the causal impact of a recent marketing campaign on product sales using historical sales data.

**Dataset Suggestions**: Find datasets on sales and marketing campaigns from Kaggle or open government datasets related to retail.

**Tasks**:
- Data Acquisition:
    - Collect historical sales data and marketing campaign details.
    - Clean and preprocess the data for analysis.

- Regression Discontinuity Design:
    - Implement regression discontinuity to analyze the effect of the marketing campaign on sales.
  
- Causal Estimation:
    - Use IBM Causal Inference 360 to estimate the causal effect of the marketing campaign on sales figures.
  
- Sensitivity Analysis:
    - Conduct sensitivity analyses to determine how robust your findings are to potential confounders.

- Visualization:
    - Create visualizations to illustrate the causal relationships and treatment effects.

**Bonus Ideas**: Explore different marketing strategies or segment the analysis by product categories to assess varied impacts.

---

**Project 3: Understanding the Impact of Air Quality on Public Health Outcomes**  
**Difficulty**: 3 (Hard)  
**Project Objective**: To investigate the causal relationship between air quality indices and hospital admission rates for respiratory diseases.

**Dataset Suggestions**: Access public health datasets and air quality data from government portals or health organizations.

**Tasks**:
- Data Integration:
    - Gather air quality data (e.g., PM2.5 levels) and hospital admission records for respiratory diseases.
    - Clean and merge the datasets based on time and geographical location.

- Instrumental Variable Analysis:
    - Utilize instrumental variable methods to address potential confounding factors affecting the relationship between air quality and health outcomes.
  
- Causal Effect Estimation:
    - Apply IBM Causal Inference 360 to estimate the causal effect of air quality on hospital admissions.
  
- Model Validation:
    - Validate the causal model through diagnostic tests and robustness checks.

- Comprehensive Reporting:
    - Develop a detailed report that includes findings, implications for public health policy, and visualizations of the causal relationships.

**Bonus Ideas**: Investigate seasonal variations in the impact of air quality on health, or integrate socioeconomic factors into the analysis to explore differential impacts.

