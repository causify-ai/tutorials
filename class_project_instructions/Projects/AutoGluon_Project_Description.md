**Description**

AutoGluon is an open-source AutoML toolkit designed to simplify the process of building machine learning models. It automates the selection of algorithms, hyperparameter tuning, and model evaluation, making it accessible for users with varying levels of expertise. Key features include:

- **Automatic Model Selection**: Quickly identifies the best algorithms for your dataset.
- **Hyperparameter Optimization**: Fine-tunes model parameters to enhance performance.
- **Ensemble Learning**: Combines multiple models to improve accuracy and robustness.
- **Support for Various Data Types**: Works with structured data, text, and images.

---

### Project 1: Predicting Housing Prices
**Difficulty**: 1 (Easy)

**Project Objective**: The goal of this project is to predict housing prices based on various features such as location, size, and amenities. Students will optimize the model to achieve the highest possible accuracy.

**Dataset Suggestions**: Look for housing datasets on Kaggle or open government portals that provide historical housing prices and features.

**Tasks**:
- **Data Ingestion**: Load the dataset into a DataFrame using Pandas.
- **Data Preprocessing**: Clean the data by handling missing values and encoding categorical features.
- **Model Training with AutoGluon**: Utilize AutoGluon to automatically train multiple regression models and select the best one.
- **Model Evaluation**: Assess model performance using metrics such as RMSE and R-squared.
- **Visualization**: Create visualizations to show the relationship between features and predicted prices.

**Bonus Ideas (Optional)**:
- Experiment with feature engineering to enhance model performance.
- Compare AutoGluon’s results against a manually tuned model to analyze differences.

---

### Project 2: Customer Churn Prediction
**Difficulty**: 2 (Medium)

**Project Objective**: This project aims to predict customer churn for a subscription-based service. Students will optimize the model to minimize false negatives, ensuring that at-risk customers are identified.

**Dataset Suggestions**: Find customer churn datasets on Kaggle or open datasets related to telecommunications or subscription services.

**Tasks**:
- **Data Loading**: Import the customer churn dataset into a Pandas DataFrame.
- **Exploratory Data Analysis (EDA)**: Conduct EDA to understand the distribution of features and identify patterns.
- **Model Training with AutoGluon**: Use AutoGluon to train classification models and identify the best-performing one for predicting churn.
- **Feature Importance Analysis**: Analyze which features are most influential in predicting churn.
- **Model Evaluation**: Evaluate the model using precision, recall, and F1-score, focusing on minimizing false negatives.

**Bonus Ideas (Optional)**:
- Implement a cost-benefit analysis to quantify the impact of reducing churn.
- Explore the effect of different sampling techniques on model performance.

---

### Project 3: Image Classification of Plant Species
**Difficulty**: 3 (Hard)

**Project Objective**: The objective is to classify images of various plant species based on their features. Students will optimize the model for accuracy while dealing with a diverse dataset with multiple classes.

**Dataset Suggestions**: Use image datasets available on Kaggle or HuggingFace that contain labeled images of different plant species.

**Tasks**:
- **Data Collection**: Download and organize the image dataset into training and validation sets.
- **Data Augmentation**: Apply techniques such as rotation, flipping, and scaling to enhance dataset diversity.
- **Model Training with AutoGluon**: Leverage AutoGluon to train deep learning models for image classification.
- **Transfer Learning**: Utilize pre-trained models and fine-tune them using AutoGluon for improved performance.
- **Model Evaluation**: Assess classification accuracy using confusion matrices and classification reports.

**Bonus Ideas (Optional)**:
- Implement a web application for real-time plant species classification using the trained model.
- Experiment with different architectures and compare their performance against the AutoGluon results.

