### Project 1: Image Classification with Transfer Learning
- **Difficulty**: 1
- **Tech Description**: Utilize `torch_xla` to leverage TPUs for efficient transfer learning on a pre-trained convolutional neural network (CNN) model for image classification tasks.
- **Project Idea**: The goal of this project is to classify images from the CIFAR-10 dataset using a pre-trained model like ResNet. Students will fine-tune the model on the dataset to achieve high accuracy while minimizing training time using TPUs via `torch_xla`. The project will explore data augmentation techniques to enhance model performance and evaluate the results using various metrics such as accuracy and F1-score.
- **Python libs**: `torch`, `torchvision`, `torch_xla`, `numpy`, `matplotlib`
- **Is it Free?**: Yes, the datasets are publicly available, and TPUs can be accessed via Google Colab for free.
- **Relevant tool (torch_xla) related Resource Links**: 
  - [Torch XLA Documentation](https://github.com/pytorch/xla)
  - [CIFAR-10 Dataset](https://www.cs.toronto.edu/~kriz/cifar.html)

---

### Project 2: Time Series Forecasting Using Recurrent Neural Networks
- **Difficulty**: 2
- **Tech Description**: Implement a recurrent neural network (RNN) model for time series forecasting while leveraging `torch_xla` to accelerate training on TPUs.
- **Project Idea**: This project aims to forecast future stock prices using historical data from the Yahoo Finance API. Students will preprocess the time series data and create an RNN model using PyTorch. By utilizing `torch_xla`, they will optimize the training process on TPUs. The project will include hyperparameter tuning, model evaluation using RMSE, and visualizing the predicted vs. actual stock prices.
- **Python libs**: `torch`, `torch_xla`, `pandas`, `numpy`, `yfinance`
- **Is it Free?**: Yes, Yahoo Finance provides free access to stock data, and TPUs can be accessed via Google Colab.
- **Relevant tool (torch_xla) related Resource Links**: 
  - [Yahoo Finance API Documentation](https://pypi.org/project/yfinance/)
  - [Torch XLA on TPUs](https://pytorch.org/xla/)

---

### Project 3: Anomaly Detection in Network Traffic
- **Difficulty**: 3
- **Tech Description**: Use `torch_xla` to implement a deep learning model for anomaly detection in network traffic data, leveraging TPUs for efficient computation.
- **Project Idea**: The aim of this project is to detect anomalies in network traffic data using the UNSW-NB15 dataset. Students will preprocess the dataset, apply feature engineering, and train an autoencoder model using `torch_xla` on TPUs to identify unusual patterns in the traffic. The project will involve evaluating the model's performance using precision, recall, and F1-score, as well as visualizing the detected anomalies.
- **Python libs**: `torch`, `torch_xla`, `pandas`, `numpy`, `matplotlib`
- **Is it Free?**: Yes, the UNSW-NB15 dataset is publicly available, and TPUs can be accessed via Google Colab.
- **Relevant tool (torch_xla) related Resource Links**: 
  - [UNSW-NB15 Dataset](https://research.unsw.edu.au/projects/unsw-nb15-dataset-1)
  - [Torch XLA GitHub Repository](https://github.com/pytorch/xla)

