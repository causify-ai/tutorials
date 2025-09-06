**Description**

Lightning-Fabric is a high-level wrapper for PyTorch that simplifies the process of building and training deep learning models. It provides a flexible framework for organizing code, managing distributed training, and handling logging and checkpointing. Key features include:

- **Modular Design**: Facilitates the organization of code into reusable components.
- **Distributed Training**: Easily scale up training across multiple GPUs or nodes.
- **Logging and Checkpointing**: Automatically manage experiment logging and model checkpoints.
- **Integration with PyTorch**: Seamlessly integrates with existing PyTorch codebases.

---

### Project 1: Image Classification of Fashion Items
**Difficulty**: 1 (Easy)  
**Project Objective**: Build a convolutional neural network (CNN) to classify images of clothing items from the Fashion MNIST dataset, optimizing for accuracy.

**Dataset Suggestions**:  
- Fashion MNIST dataset available on Kaggle: [Fashion MNIST](https://www.kaggle.com/datasets/zalando-research/fashionmnist)

**Tasks**:  
- **Data Preparation**: Load the Fashion MNIST dataset and preprocess images (normalization, resizing).
- **Model Definition**: Create a CNN architecture using Lightning-Fabric.
- **Training**: Train the model and monitor performance metrics (accuracy and loss).
- **Evaluation**: Evaluate the model on a test set and visualize classification results with confusion matrices.
- **Logging**: Implement logging to track training progress using Lightning-Fabric’s built-in features.

---

### Project 2: Text Classification for Sentiment Analysis
**Difficulty**: 2 (Medium)  
**Project Objective**: Develop a text classification model to predict sentiment (positive, negative, neutral) from movie reviews, optimizing for F1-score.

**Dataset Suggestions**:  
- IMDB Movie Reviews dataset available on Kaggle: [IMDB Dataset](https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews)

**Tasks**:  
- **Data Loading**: Load the IMDB dataset and preprocess text (tokenization, padding).
- **Model Architecture**: Construct an LSTM or Transformer-based model using Lightning-Fabric.
- **Training and Fine-tuning**: Train the model with hyperparameter tuning and regularization techniques.
- **Evaluation**: Assess model performance using F1-score and confusion matrices.
- **Logging and Checkpointing**: Use Lightning-Fabric to log metrics and save model checkpoints during training.

---

### Project 3: Time Series Forecasting of Stock Prices
**Difficulty**: 3 (Hard)  
**Project Objective**: Create a forecasting model to predict stock prices using historical data, optimizing for RMSE (Root Mean Square Error).

**Dataset Suggestions**:  
- Yahoo Finance API for historical stock price data (e.g., Apple Inc.): [Yahoo Finance](https://finance.yahoo.com/quote/AAPL/history?p=AAPL)

**Tasks**:  
- **Data Acquisition**: Use the Yahoo Finance API to gather historical stock price data.
- **Data Preprocessing**: Clean and preprocess the data (handling missing values, scaling).
- **Model Development**: Build a recurrent neural network (RNN) or a hybrid model using Lightning-Fabric.
- **Training and Validation**: Train the model and validate using a rolling-window approach.
- **Performance Evaluation**: Evaluate the model's performance using RMSE and visualize predictions against actual prices.
- **Logging and Experiment Tracking**: Implement logging and experiment tracking with Lightning-Fabric for reproducibility.

**Bonus Ideas (Optional)**:  
- For Project 1: Experiment with different CNN architectures (ResNet, DenseNet) and compare performance.
- For Project 2: Explore transfer learning by using pre-trained models like BERT for enhanced performance.
- For Project 3: Integrate external features like trading volume or economic indicators to improve forecasting accuracy.

