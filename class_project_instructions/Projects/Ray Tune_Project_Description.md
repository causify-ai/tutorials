### Project 1: Hyperparameter Optimization for Wine Quality Prediction
- **Difficulty**: 1
- **Tech Description**: Ray Tune is used to efficiently explore hyperparameter spaces for machine learning models to improve their performance.
- **Project Idea**: The goal of this project is to predict the quality of wines based on physicochemical tests using the Wine Quality dataset from the UCI Machine Learning Repository. Students will implement a regression model (e.g., Random Forest or Gradient Boosting) and utilize Ray Tune for hyperparameter optimization. By systematically tuning parameters such as learning rate, max depth, and number of estimators, students will evaluate the model's performance using metrics like Mean Squared Error (MSE). The project will culminate in a comparative analysis of model performance before and after hyperparameter optimization.
- **Python libs**: ray[tune], pandas, scikit-learn, matplotlib, seaborn
- **Is it Free?**: Yes, all libraries and the dataset are freely available online.
- **Relevant tool (Ray Tune) related Resource Links**: 
  - [Ray Tune Documentation](https://docs.ray.io/en/latest/tune/index.html)
  - [Wine Quality Dataset](https://archive.ics.uci.edu/ml/datasets/wine+quality)

---

### Project 2: Automated Hyperparameter Tuning for Time Series Forecasting
- **Difficulty**: 2
- **Tech Description**: Ray Tune is employed to optimize hyperparameters for time series forecasting models using a distributed approach.
- **Project Idea**: This project focuses on predicting future stock prices using historical data from Yahoo Finance. Students will use ARIMA or Facebook Prophet models and leverage Ray Tune to optimize hyperparameters such as seasonal order and trend. The objective is to improve the forecasting accuracy by fine-tuning model parameters based on historical stock price data. The performance will be evaluated using metrics like RMSE and visualized through forecasting plots. Students will also compare the results against a baseline model to demonstrate the effectiveness of hyperparameter tuning.
- **Python libs**: ray[tune], pandas, yfinance, statsmodels, matplotlib
- **Is it Free?**: Yes, all libraries and the Yahoo Finance API are free to use.
- **Relevant tool (Ray Tune) related Resource Links**: 
  - [Ray Tune Time Series Example](https://docs.ray.io/en/latest/tune/examples/advanced.html)
  - [Yahoo Finance API Documentation](https://pypi.org/project/yfinance/)

---

### Project 3: Multi-Objective Hyperparameter Optimization for Image Classification
- **Difficulty**: 3
- **Tech Description**: Ray Tune is used for multi-objective optimization to balance accuracy and model size in image classification tasks.
- **Project Idea**: In this advanced project, students will classify images from the CIFAR-10 dataset using a pre-trained Convolutional Neural Network (CNN) and optimize hyperparameters using Ray Tune for both accuracy and model size. The goal is to find a sweet spot between achieving high classification accuracy while minimizing model complexity. Students will set up a multi-objective optimization problem where Ray Tune will help navigate the trade-offs between the two objectives. The project will include an evaluation of the optimized model on a validation set and a discussion on the implications of model complexity in deployment scenarios.
- **Python libs**: ray[tune], tensorflow, keras, numpy, matplotlib
- **Is it Free?**: Yes, all libraries and the CIFAR-10 dataset are publicly available for free.
- **Relevant tool (Ray Tune) related Resource Links**: 
  - [Ray Tune Multi-Objective Optimization](https://docs.ray.io/en/latest/tune/tutorials/multi_objective.html)
  - [CIFAR-10 Dataset](https://www.cs.toronto.edu/~kriz/cifar.html)

