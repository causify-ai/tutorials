**Description**

DoWhy is a Python library designed for causal inference that allows users to identify and estimate causal effects from observational data. It provides a unified framework for defining causal graphs, estimating treatment effects, and performing sensitivity analysis. DoWhy is particularly useful for researchers and data scientists looking to understand the causal relationships between variables in their datasets.

Technologies Used
DoWhy

- Facilitates causal inference through graphical models and potential outcomes framework.
- Offers a structured approach to defining causal graphs and identifying confounding variables.
- Supports various estimation methods, including regression adjustment, matching, and instrumental variables.
- Enables sensitivity analysis to assess the robustness of causal estimates.

---

**Project 1: Analyzing the Impact of Education on Income (Difficulty: 1)**

**Project Objective:**  
Determine the causal effect of education level on annual income using observational data.

**Dataset Suggestions:**  
- Use the "Adult Income Dataset" available on Kaggle ([Adult Income](https://www.kaggle.com/uciml/adult-census-income)).

**Tasks:**
- **Define the Causal Graph:**  
  Construct a causal graph to represent the relationship between education, income, and potential confounders like age and job type.

- **Estimate Treatment Effect:**  
  Use DoWhy to estimate the causal effect of education on income, applying regression adjustment to control for confounding variables.

- **Conduct Sensitivity Analysis:**  
  Evaluate the robustness of the causal estimates by performing sensitivity analysis to check how changes in assumptions affect results.

- **Visualize Results:**  
  Create visualizations to illustrate the estimated causal effect and the sensitivity analysis findings.

---

**Project 2: Evaluating the Effect of Exercise on Mental Health (Difficulty: 2)**

**Project Objective:**  
Assess the causal relationship between the frequency of exercise and reported mental health outcomes.

**Dataset Suggestions:**  
- Use the "Mental Health in Tech Survey" dataset on Kaggle ([Mental Health in Tech](https://www.kaggle.com/osmi/mental-health-in-tech-survey)).

**Tasks:**
- **Define the Causal Framework:**  
  Develop a causal graph that includes exercise frequency, mental health status, and potential confounders such as age, gender, and employment status.

- **Estimate Causal Effects:**  
  Utilize DoWhy to estimate the causal effect of exercise on mental health using matching techniques to control for confounders.

- **Sensitivity Analysis:**  
  Implement sensitivity analysis to assess how robust the causal conclusions are to unobserved confounding.

- **Interpret and Report Findings:**  
  Summarize the findings in a report, discussing the implications of the causal relationship and potential policy recommendations.

---

**Project 3: Understanding the Impact of Advertising on Sales (Difficulty: 3)**

**Project Objective:**  
Investigate the causal effect of advertising spend on product sales while accounting for confounding factors such as seasonality and market trends.

**Dataset Suggestions:**  
- Use the "Advertising Dataset" available on Kaggle ([Advertising](https://www.kaggle.com/ashishpatel26/advertising-data)).

**Tasks:**
- **Construct the Causal Graph:**  
  Create a detailed causal graph that includes advertising spend, sales, and confounding factors like seasonality and competitor actions.

- **Estimate Treatment Effects:**  
  Apply DoWhy to estimate the causal effect of advertising on sales using advanced techniques such as instrumental variables to account for endogeneity.

- **Perform Robustness Checks:**  
  Conduct sensitivity analysis to evaluate the impact of unobserved confounding on the causal estimates.

- **Model Comparison:**  
  Compare the results obtained from different causal estimation methods (e.g., regression vs instrumental variables) and discuss the implications of discrepancies.

- **Visualization and Reporting:**  
  Visualize the causal relationships and present a comprehensive report detailing the methodology, findings, and recommendations for advertising strategies.

**Bonus Ideas (Optional):**  
- For Project 1, consider exploring the interaction effects of education and age on income.  
- For Project 2, analyze the impact of different types of exercise (e.g., aerobic vs strength training) on mental health outcomes.  
- For Project 3, extend the analysis to include a time series component to assess the long-term effects of advertising on sales trends.

