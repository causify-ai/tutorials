**Description**

In this project, students will use AutoGluon, an open-source library that automates machine learning tasks, to build and evaluate models with minimal coding effort. AutoGluon supports various data types and tasks, including tabular data, images, and text, allowing users to efficiently tackle machine learning problems. 

Technologies Used
AutoGluon

- Automates the training and tuning of machine learning models.
- Supports multiple data types and tasks (classification, regression, object detection, etc.).
- Provides built-in capabilities for model ensembling and stacking.
- Offers easy-to-use APIs for quick experimentation and deployment.


### Project 1: Predicting House Prices (Difficulty: 1)

**Project Objective**: 
Develop a model to predict house prices based on various features such as location, size, and amenities. The goal is to optimize the prediction accuracy using AutoGluon.

**Dataset Suggestions**: 
- **Dataset**: Ames Housing Dataset
- **Source**: Available on Kaggle [Ames Housing Dataset](https://www.kaggle.com/datasets/prestonvong/ames-housing-data)

**Tasks**:
- **Data Preprocessing**: Load the dataset and handle missing values and categorical features using AutoGluon's preprocessing capabilities.
- **Model Training**: Utilize AutoGluon to train multiple regression models automatically.
- **Hyperparameter Tuning**: Leverage AutoGluon’s built-in hyperparameter optimization to improve model performance.
- **Model Evaluation**: Evaluate the models using metrics like RMSE and R-squared.
- **Visualization**: Visualize the predicted vs. actual prices using Matplotlib.

### Project 2: Customer Churn Prediction (Difficulty: 2)

**Project Objective**: 
Create a classification model to predict customer churn for a telecom company based on customer demographics and service usage. The goal is to identify at-risk customers to improve retention strategies.

**Dataset Suggestions**: 
- **Dataset**: Telco Customer Churn
- **Source**: Available on Kaggle [Telco Customer Churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)

**Tasks**:
- **Data Exploration**: Perform exploratory data analysis to understand feature distributions and relationships.
- **Feature Engineering**: Create new features and encode categorical variables using AutoGluon’s feature handling capabilities.
- **Model Training**: Use AutoGluon to train various classification models and compare their performance.
- **Model Interpretation**: Analyze feature importance to understand which factors contribute most to churn.
- **Deployment**: Save the best-performing model for future predictions and demonstrate how to use it for new customer data.

### Project 3: Image Classification for Plant Disease Detection (Difficulty: 3)

**Project Objective**: 
Develop a deep learning model to classify images of plants and detect diseases. The goal is to achieve high accuracy in identifying healthy vs. diseased plants using AutoGluon.

**Dataset Suggestions**: 
- **Dataset**: PlantVillage Dataset
- **Source**: Available on Kaggle [PlantVillage Dataset](https://www.kaggle.com/datasets/emmarex/plantdisease)

**Tasks**:
- **Data Preparation**: Load the dataset and preprocess images (resizing, normalization) for model training.
- **Model Selection**: Utilize AutoGluon’s image classification capabilities to automatically select and train the best models.
- **Transfer Learning**: Fine-tune pre-trained models on the dataset to improve classification performance.
- **Performance Evaluation**: Evaluate models using accuracy, precision, recall, and F1-score metrics.
- **Visualization**: Create visualizations of misclassified images and analyze the model’s performance on different classes.

**Bonus Ideas (Optional)**:
- For Project 1: Implement cross-validation to ensure robustness in model performance.
- For Project 2: Compare the AutoGluon model with traditional models (like Logistic Regression) to highlight the advantages of automation.
- For Project 3: Explore data augmentation techniques to improve the model's ability to generalize on unseen data.

