### Project 1: Hyperparameter Optimization for Time Series Forecasting
- **Difficulty:** 1
- **Tech Description:** Optuna is utilized to optimize hyperparameters for a time series forecasting model, improving prediction accuracy.
- **Project Idea:** This project aims to forecast future sales of a retail store using historical sales data. The student will implement a seasonal ARIMA model and use Optuna to optimize its hyperparameters, such as the order of differencing and seasonal parameters. The goal is to minimize forecasting error by finding the best set of hyperparameters through a systematic search. The student will evaluate model performance using metrics like Mean Absolute Error (MAE) and visualize the forecast against actual sales.
- **Python libs:** pandas, statsmodels, Optuna, matplotlib, scikit-learn
- **Is it Free?** Yes, all libraries and datasets used in this project are freely available.
- **Relevant tool (Optuna) related Resource Links:** 
  - [Optuna Documentation](https://optuna.readthedocs.io/en/stable/)
  - [Time Series Forecasting with ARIMA](https://www.statsmodels.org/stable/examples/notebooks/generated/tsa_arima.html)

---

### Project 2: Optimizing a Machine Learning Pipeline for Credit Scoring
- **Difficulty:** 2
- **Tech Description:** Optuna is applied to tune hyperparameters of a machine learning pipeline for credit scoring, enhancing model performance.
- **Project Idea:** This project focuses on developing a credit scoring model using the UCI Credit Card Default dataset. The student will create a machine learning pipeline that includes preprocessing steps (like normalization and encoding) and a classifier (e.g., Random Forest). Optuna will be used to optimize hyperparameters for both the preprocessing and the classifier, aiming to improve the F1 score. The final model will be evaluated on a test set and compared against a baseline model.
- **Python libs:** pandas, scikit-learn, Optuna, imbalanced-learn, matplotlib
- **Is it Free?** Yes, all libraries and datasets are freely accessible.
- **Relevant tool (Optuna) related Resource Links:** 
  - [Optuna and Scikit-learn Integration](https://optuna.readthedocs.io/en/stable/tutorial/10-keyfeatures/002_sklearn.html)
  - [UCI Credit Card Default Dataset](https://archive.ics.uci.edu/ml/datasets/default+of+credit+card+clients)

---

### Project 3: Model Selection for Image Classification with Transfer Learning
- **Difficulty:** 3
- **Tech Description:** Optuna is employed to optimize the selection of pre-trained models and their hyperparameters for image classification tasks.
- **Project Idea:** This project aims to classify images of flowers using the Oxford Flowers 102 dataset. The student will leverage transfer learning with various pre-trained models (e.g., VGG16, ResNet50) and use Optuna to select the best model and optimize hyperparameters such as learning rate and batch size. The goal is to achieve the highest accuracy on the validation set while also implementing early stopping to prevent overfitting. The results will be compared against standard benchmarks for the dataset.
- **Python libs:** TensorFlow, Keras, Optuna, numpy, matplotlib
- **Is it Free?** Yes, all libraries and datasets used are freely available.
- **Relevant tool (Optuna) related Resource Links:** 
  - [Optuna for Keras](https://optuna.readthedocs.io/en/stable/tutorial/10-keyfeatures/005_keras.html)
  - [Oxford Flowers 102 Dataset](http://www.robots.ox.ac.uk/~vgg/data/flowers/102/)

