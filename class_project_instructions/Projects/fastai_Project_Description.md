**Description**

In this project, students will utilize fastai, a high-level library built on PyTorch, to create and train deep learning models efficiently. It simplifies the process of building neural networks while providing powerful features for various tasks, including image classification, text processing, and tabular data analysis.

Technologies Used
fastai

- Facilitates quick model prototyping with built-in data loaders and transforms.
- Supports transfer learning with pre-trained models for faster convergence.
- Provides comprehensive tools for model evaluation, visualization, and interpretation.

---

### Project 1: Image Classification of Plant Diseases (Difficulty: 1)

**Project Objective**  
Develop a model that classifies images of plants to detect various diseases, optimizing for accuracy in classification.

**Dataset Suggestions**  
- **PlantVillage Dataset**: Available on Kaggle, containing over 54,000 images of healthy and diseased plant leaves.
- Link: [PlantVillage Dataset on Kaggle](https://www.kaggle.com/datasets/emmarex/plantdisease)

**Tasks**  
- **Data Preparation**: Load the dataset and perform necessary preprocessing steps like resizing and normalization.
- **Model Selection**: Use a pre-trained ResNet model for transfer learning to classify plant diseases.
- **Training**: Fine-tune the model on the PlantVillage dataset and monitor accuracy during training.
- **Evaluation**: Evaluate model performance using confusion matrices and classification reports.
- **Visualization**: Visualize misclassified images and model predictions to understand errors.

---

### Project 2: Sentiment Analysis of Movie Reviews (Difficulty: 2)

**Project Objective**  
Create a sentiment analysis model to classify movie reviews as positive or negative, focusing on improving F1 score and precision.

**Dataset Suggestions**  
- **IMDb Movie Reviews**: Available on Kaggle, containing 50,000 reviews labeled as positive or negative.
- Link: [IMDb Movie Reviews on Kaggle](https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews)

**Tasks**  
- **Data Loading**: Load the IMDb dataset and perform text preprocessing (tokenization, cleaning).
- **Text Embedding**: Utilize fastai’s text module to create embeddings for the reviews.
- **Model Building**: Implement a text classification model using a pre-trained language model (e.g., AWD-LSTM).
- **Training and Tuning**: Train the model and experiment with hyperparameter tuning to optimize the F1 score.
- **Evaluation**: Assess model performance using precision, recall, and F1 score metrics.

---

### Project 3: Predicting House Prices using Tabular Data (Difficulty: 3)

**Project Objective**  
Develop a model to predict house prices based on various features, focusing on reducing mean absolute error (MAE).

**Dataset Suggestions**  
- **House Prices - Advanced Regression Techniques**: Available on Kaggle, with detailed features for over 1,400 houses.
- Link: [House Prices Dataset on Kaggle](https://www.kaggle.com/c/house-prices-advanced-regression-techniques/data)

**Tasks**  
- **Data Exploration**: Perform exploratory data analysis (EDA) to understand the distribution of features and target variable.
- **Feature Engineering**: Create new features based on existing data (e.g., log transformation, one-hot encoding).
- **Model Training**: Use fastai’s tabular data module to set up and train a regression model (e.g., TabularModel).
- **Hyperparameter Optimization**: Implement techniques like learning rate finder and cross-validation to enhance model performance.
- **Evaluation**: Evaluate the model using metrics like MAE and visualize feature importance to understand contributions to predictions.

**Bonus Ideas (Optional)**  
- For Project 1, consider implementing a web app using Streamlit to showcase the model's predictions.
- For Project 2, explore multi-class sentiment classification by expanding the dataset to include neutral reviews.
- For Project 3, compare the performance of different regression algorithms (e.g., Random Forest, XGBoost) against the fastai model.

