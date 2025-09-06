**Description**

CausalPy is a Python library designed for causal inference, enabling users to estimate causal effects from observational data. It provides tools for identifying and estimating causal relationships using methods such as propensity score matching, regression discontinuity, and instrumental variables. CausalPy aids in understanding how changes in one variable can influence another, making it an essential tool for data scientists focused on causal analysis.

---

### Project 1: Analyzing the Impact of Educational Programs on Student Performance

**Difficulty**: 1 (Easy)

**Project Objective**: The goal is to evaluate the effect of a specific educational intervention (e.g., tutoring programs) on student performance in standardized tests.

**Dataset Suggestions**: Look for datasets on educational performance available on Kaggle, or check out open government education portals.

**Tasks**:
- **Data Collection**: Gather data on student performance, demographic information, and details about the educational program.
- **Preprocessing**: Clean the dataset, handle missing values, and ensure the data is suitable for analysis.
- **Exploratory Data Analysis (EDA)**: Perform EDA to understand the distributions and relationships in the data.
- **Causal Inference Setup**: Use CausalPy to identify the treatment group (students who participated in the program) and the control group (students who did not).
- **Estimate Causal Effect**: Apply propensity score matching to estimate the causal effect of the program on student performance.
- **Interpret Results**: Analyze the results and visualize the causal effect using appropriate plots.

---

### Project 2: Evaluating the Effect of Marketing Campaigns on Sales Performance

**Difficulty**: 2 (Medium)

**Project Objective**: The project aims to measure the causal impact of various marketing campaigns on product sales over a defined period.

**Dataset Suggestions**: Search for sales and marketing campaign datasets on Kaggle or utilize public datasets from marketing research organizations.

**Tasks**:
- **Data Acquisition**: Collect sales data and marketing campaign data, including details like campaign type, duration, and expenditure.
- **Data Cleaning and Preparation**: Clean the dataset and create relevant features to enhance the analysis.
- **Exploratory Analysis**: Conduct EDA to visualize sales trends and marketing campaign effectiveness.
- **Causal Model Specification**: Use CausalPy to specify a causal model, identifying potential confounders and control variables.
- **Causal Estimation**: Implement regression discontinuity or instrumental variable methods to estimate the causal effect of campaigns on sales.
- **Evaluate and Present Findings**: Summarize the findings, providing insights into which campaigns were most effective and visualizing the causal impacts.

---

### Project 3: Analyzing the Effect of Remote Work on Employee Productivity

**Difficulty**: 3 (Hard)

**Project Objective**: The aim is to investigate the causal relationship between the shift to remote work and employee productivity levels across different sectors.

**Dataset Suggestions**: Utilize datasets from public labor statistics or research organizations that track productivity metrics pre- and post-remote work policies.

**Tasks**:
- **Data Gathering**: Collect data on employee productivity metrics, work environment changes, and demographic information.
- **Data Wrangling**: Process the data, ensuring that it is clean and structured for causal analysis.
- **In-depth EDA**: Conduct a thorough exploratory analysis to identify trends in productivity before and after the remote work transition.
- **Causal Inference Framework**: Use CausalPy to set up a causal framework, identifying treatment and control groups based on remote work adoption.
- **Advanced Causal Estimation**: Apply advanced causal inference techniques such as difference-in-differences or synthetic control methods to analyze the impact on productivity.
- **Interpretation and Visualization**: Present the findings, emphasizing the causal relationships and visualizing the changes in productivity across different sectors.

**Bonus Ideas (Optional)**: 
- For Project 1, consider comparing the effects of different types of educational interventions.
- For Project 2, analyze the long-term effects of marketing campaigns on customer retention and lifetime value.
- For Project 3, explore the impact of remote work on employee well-being and job satisfaction as additional metrics.

