**Description**

Ax is a powerful platform designed for optimizing experiments and machine learning models through advanced Bayesian optimization techniques. It provides a flexible framework for defining and managing optimization problems, enabling users to efficiently explore hyperparameter spaces and make data-driven decisions. 

Features:
- Supports various optimization tasks, including hyperparameter tuning, experimental design, and multi-objective optimization.
- Integrates seamlessly with popular machine learning libraries like PyTorch and TensorFlow.
- Provides a user-friendly interface for defining search spaces and constraints.
- Facilitates tracking and visualization of optimization results.

---

### Project 1: Hyperparameter Optimization for a Classification Model
**Difficulty**: 1

**Project Objective**: Optimize hyperparameters for a Random Forest classifier to improve accuracy on the Adult Income dataset, predicting whether an individual earns more than $50,000 a year.

**Dataset Suggestions**: 
- Adult Income dataset from UCI Machine Learning Repository ([link](https://archive.ics.uci.edu/ml/datasets/adult))

**Tasks**:
- **Data Preprocessing**: Load the dataset, handle missing values, and encode categorical features using one-hot encoding.
- **Define Search Space**: Use Ax to define hyperparameter bounds for the Random Forest model, including the number of trees and maximum depth.
- **Optimization Process**: Implement Ax to perform Bayesian optimization, iterating through hyperparameter combinations to find the best set.
- **Model Training**: Train the Random Forest model with the optimized hyperparameters and evaluate its accuracy on a test set.
- **Results Visualization**: Visualize the optimization process and final model performance using Matplotlib.

---

### Project 2: Multi-Objective Optimization for a Regression Model
**Difficulty**: 2

**Project Objective**: Optimize hyperparameters for a Gradient Boosting Regressor to minimize both the Mean Absolute Error (MAE) and the model complexity (number of estimators).

**Dataset Suggestions**: 
- California Housing Prices dataset from Kaggle ([link](https://www.kaggle.com/c/california-housing-prices/data))

**Tasks**:
- **Data Preparation**: Load the dataset, normalize features, and handle missing values.
- **Define Multi-Objective Space**: Use Ax to set up a multi-objective optimization problem targeting both MAE and number of estimators.
- **Run Optimization**: Utilize Ax’s optimization features to explore hyperparameters like learning rate and maximum depth while evaluating both objectives.
- **Model Evaluation**: Assess the performance of the optimized model on a validation set, ensuring a balance between accuracy and complexity.
- **Visualize Trade-offs**: Create a Pareto front plot to visualize the trade-offs between the two objectives.

---

### Project 3: Adaptive Experimentation in Marketing Campaigns
**Difficulty**: 3

**Project Objective**: Design an adaptive marketing campaign that optimizes the allocation of budget across different channels to maximize customer engagement while minimizing costs.

**Dataset Suggestions**: 
- Marketing Campaign dataset from Kaggle ([link](https://www.kaggle.com/datasets/rodsaldanha/marketing-campaign))

**Tasks**:
- **Data Exploration**: Load and explore the dataset to understand customer demographics and engagement metrics.
- **Define Optimization Problem**: Use Ax to define an optimization problem where the budget allocation across channels (e.g., email, social media, direct mail) is the variable to optimize.
- **Simulate Campaign Outcomes**: Create a simulation model to predict customer engagement based on budget allocation and historical data.
- **Run Adaptive Optimization**: Implement Ax to perform adaptive experimentation, adjusting budget allocations in real-time based on engagement feedback.
- **Analyze Results**: Evaluate the effectiveness of the campaign through metrics like Return on Investment (ROI) and visualize the optimization results.

**Bonus Ideas**: 
- For Project 1: Compare the optimized model against a baseline model using default hyperparameters.
- For Project 2: Experiment with different regression algorithms (e.g., Support Vector Regression) and compare their optimization results.
- For Project 3: Introduce additional constraints, such as maximum budget limits for specific channels, and observe the impact on engagement.

