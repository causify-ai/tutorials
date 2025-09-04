### Tech Description: DoWhy
DoWhy is a Python library designed for causal inference, enabling users to understand the causal relationships in their data. It provides a framework for modeling causal graphs and conducting causal analyses through various methods. Key features include:
- Causal graph creation and visualization
- Estimation of causal effects using different methods (e.g., propensity score matching, regression adjustment)
- Robustness checks for causal assumptions
- Integration with popular data science libraries like Pandas and Statsmodels

### Project Blueprint

---

#### Project 1: Analyzing the Impact of Education on Income
**Difficulty**: 1 (Easy)

**Project Objective**: Determine the causal effect of education level on annual income, optimizing for a clearer understanding of how educational attainment influences earnings.

**Dataset Suggestions**: Use open datasets from government labor statistics or Kaggle that include demographic information, education levels, and income data.

**Step-by-Step Plan**:
1. **Data Collection**: Download the dataset from a public source like Kaggle or government labor statistics.
2. **Feature Engineering**: Clean the dataset, create categorical variables for education level, and normalize income data.
3. **Model Training**: Use DoWhy to create a causal graph representing the relationship between education and income.
4. **Use of the Tool**: Apply DoWhy's estimation methods (e.g., regression adjustment) to estimate the causal effect of education on income.
5. **Evaluation Metrics**: Analyze the estimated effect size and confidence intervals.
6. **Visualization**: Create visualizations of the causal graph and the estimated effects using Matplotlib or Seaborn.

**Bonus Ideas**: Explore additional variables such as geographic location or industry to see how they might moderate the effect of education on income.

---

#### Project 2: Evaluating the Effect of Marketing Campaigns on Sales
**Difficulty**: 2 (Medium)

**Project Objective**: Assess the causal impact of different marketing campaigns on product sales, optimizing for marketing resource allocation.

**Dataset Suggestions**: Look for datasets on Kaggle that include sales data along with details of marketing campaigns, such as social media ads or email marketing.

**Step-by-Step Plan**:
1. **Data Collection**: Gather data from Kaggle, ensuring it includes sales figures and detailed marketing campaign information.
2. **Feature Engineering**: Create features for campaign types, timings, and customer demographics.
3. **Model Training**: Construct a causal graph to represent the relationship between marketing efforts and sales outcomes.
4. **Use of the Tool**: Use DoWhy to estimate the causal effect of marketing campaigns on sales, employing methods like propensity score matching.
5. **Evaluation Metrics**: Evaluate using metrics such as the Average Treatment Effect (ATE) and check for robustness.
6. **Visualization**: Present findings through dashboards or reports that highlight the effectiveness of each campaign.

**Bonus Ideas**: Compare the results across different product categories or geographic regions to identify which campaigns are most effective.

---

#### Project 3: Investigating the Causal Factors of Air Quality on Public Health
**Difficulty**: 3 (Hard)

**Project Objective**: Explore the causal relationships between air quality indices and public health outcomes, optimizing for policy recommendations.

**Dataset Suggestions**: Utilize open datasets from government environmental agencies or health organizations that provide air quality metrics and health statistics.

**Step-by-Step Plan**:
1. **Data Collection**: Access public datasets that include air quality indices (e.g., PM2.5 levels) and health outcome measures (e.g., hospital admissions for respiratory issues).
2. **Feature Engineering**: Process the data to create time-series features, normalize health outcomes, and segment by demographic factors.
3. **Model Training**: Develop a causal graph that represents the hypothesized relationships between air quality and health outcomes.
4. **Use of the Tool**: Use DoWhy to analyze the causal impact of air quality on health, applying methods such as instrumental variables.
5. **Evaluation Metrics**: Measure the causal effect size and conduct sensitivity analyses to test the robustness of the findings.
6. **Visualization**: Create a comprehensive report or dashboard that visualizes the causal relationships and suggests actionable insights for policymakers.

**Bonus Ideas**: Attempt to integrate additional variables like socioeconomic status or pre-existing health conditions to further refine the analysis and recommendations.

--- 

These projects are designed to give students a well-rounded experience in causal inference using DoWhy, while allowing them to explore different domains and complexity levels.

