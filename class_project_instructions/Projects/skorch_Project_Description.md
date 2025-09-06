**Description**

In this project, students will leverage Skorch, a high-level wrapper around PyTorch, to simplify the process of training neural networks while integrating seamlessly with scikit-learn. Skorch enables students to utilize the power of PyTorch while maintaining the familiar scikit-learn interface, making it easier to build, train, and evaluate deep learning models. 

Technologies Used
Skorch

- Provides a simple interface for PyTorch models, allowing users to fit, predict, and score models in a scikit-learn style.
- Supports various neural network architectures and hyperparameter tuning.
- Facilitates easy integration with scikit-learn utilities such as pipelines and cross-validation.

---

### Project 1: Image Classification with CNNs (Difficulty: 1)

**Project Objective:**  
Create a convolutional neural network (CNN) to classify images from the CIFAR-10 dataset, aiming for high accuracy on the validation set.

**Dataset Suggestions:**  
- CIFAR-10 dataset available on Kaggle: [CIFAR-10 Dataset](https://www.kaggle.com/c/cifar-10)

**Tasks:**
- **Data Loading and Preprocessing:**  
  Load the CIFAR-10 dataset using torchvision transforms for normalization and augmentation.
  
- **Model Definition:**  
  Define a simple CNN architecture using PyTorch, including convolutional layers, activation functions, and pooling layers.

- **Training with Skorch:**  
  Utilize Skorch to train the CNN model, specifying the criterion, optimizer, and metrics for evaluation.

- **Evaluation:**  
  Evaluate model performance on the validation set and visualize results using confusion matrices and accuracy scores.

- **Hyperparameter Tuning:**  
  Experiment with different hyperparameters (learning rate, batch size) to optimize model performance.

**Bonus Ideas (Optional):**  
- Implement data augmentation techniques to improve model robustness.  
- Compare performance with a pre-trained model using transfer learning.

---

### Project 2: Time Series Forecasting with LSTM (Difficulty: 2)

**Project Objective:**  
Develop an LSTM model to forecast future stock prices based on historical data from the Yahoo Finance API, optimizing for minimal prediction error.

**Dataset Suggestions:**  
- Use Yahoo Finance API to obtain historical stock price data for a specific company (e.g., Apple Inc. - AAPL).

**Tasks:**
- **Data Collection:**  
  Utilize the Yahoo Finance API to gather historical stock price data and preprocess it for LSTM input.

- **Data Preparation:**  
  Create sequences of past stock prices to use as input features for the LSTM model.

- **Model Building:**  
  Construct an LSTM model using Skorch, defining the architecture with appropriate layers (LSTM, Dense).

- **Training and Evaluation:**  
  Train the model using Skorch and evaluate performance with metrics like Mean Absolute Error (MAE) on a test set.

- **Forecasting:**  
  Generate future stock price predictions and visualize the results against actual historical prices.

**Bonus Ideas (Optional):**  
- Integrate additional features such as trading volume or moving averages.  
- Implement a more complex architecture with multiple LSTM layers or attention mechanisms.

---

### Project 3: Text Classification with Transformers (Difficulty: 3)

**Project Objective:**  
Build a text classification model using transformer architectures to classify movie reviews from the IMDb dataset, aiming for high F1-score.

**Dataset Suggestions:**  
- IMDb Movie Reviews dataset available on Kaggle: [IMDb Dataset](https://www.kaggle.com/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews)

**Tasks:**
- **Data Loading and Preprocessing:**  
  Load the IMDb dataset and preprocess text data (tokenization, padding) using Hugging Face's Transformers library.

- **Model Definition:**  
  Define a transformer-based model (e.g., BERT) using PyTorch, adapting the architecture for classification tasks.

- **Training with Skorch:**  
  Utilize Skorch to manage the training loop, including loss functions and metrics for evaluation.

- **Evaluation and Analysis:**  
  Evaluate model performance using F1-score and confusion matrices, analyzing misclassifications.

- **Fine-Tuning:**  
  Experiment with fine-tuning hyperparameters and model architecture to improve classification performance.

**Bonus Ideas (Optional):**  
- Implement a multi-class classification approach to categorize reviews into sentiment levels (positive, negative, neutral).  
- Compare results with traditional machine learning classifiers (e.g., SVM, Random Forest) on the same dataset.

