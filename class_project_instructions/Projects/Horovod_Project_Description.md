### Project 1: Scalable Image Classification with Horovod
- **Difficulty:** 1
- **Tech Description:** Horovod is utilized to distribute the training of a pre-trained convolutional neural network (CNN) across multiple GPUs to speed up image classification tasks.
- **Project Idea:** The goal of this project is to classify images from the CIFAR-10 dataset using a pre-trained ResNet model. Students will leverage Horovod to parallelize the training process across multiple GPUs, significantly reducing training time while achieving high accuracy. The project will involve data preprocessing, model loading, and evaluation of the model’s performance against a baseline single-GPU training run.
- **Python libs:** TensorFlow, Horovod, NumPy, Matplotlib, scikit-learn
- **Is it Free?** Yes, all libraries and the CIFAR-10 dataset are freely available.
- **Relevant tool (Horovod) related Resource Links:** 
  - [Horovod Documentation](https://horovod.readthedocs.io/en/stable/)
  - [CIFAR-10 Dataset](https://www.cs.toronto.edu/~kriz/cifar.html)

---

### Project 2: Distributed Time Series Forecasting
- **Difficulty:** 2
- **Tech Description:** Horovod facilitates distributed training of a time series forecasting model using LSTM networks on multiple GPUs to improve prediction accuracy.
- **Project Idea:** This project aims to forecast stock prices using historical data from Yahoo Finance. Students will preprocess the data, create LSTM models, and utilize Horovod to enable distributed training across multiple GPUs. The focus will be on optimizing the model's hyperparameters and comparing the performance of the distributed model against a single-GPU version. Students will analyze the results to draw conclusions about the efficiency of distributed training for time series data.
- **Python libs:** TensorFlow, Horovod, Pandas, NumPy, Matplotlib
- **Is it Free?** Yes, all libraries and the Yahoo Finance data are freely accessible.
- **Relevant tool (Horovod) related Resource Links:** 
  - [Horovod GitHub Repository](https://github.com/horovod/horovod)
  - [Yahoo Finance API](https://pypi.org/project/yfinance/)

---

### Project 3: Distributed Anomaly Detection in Network Traffic
- **Difficulty:** 3
- **Tech Description:** Horovod is employed to distribute the training of an autoencoder model for detecting anomalies in large-scale network traffic datasets.
- **Project Idea:** The objective of this project is to detect anomalies in network traffic data using the UNSW-NB15 dataset. Students will implement an autoencoder model to learn the normal patterns of network traffic and identify anomalies. By utilizing Horovod, they will distribute the training process across multiple GPUs to handle the large dataset efficiently. The project will include data preprocessing, model training, and evaluation of anomaly detection performance, as well as a comparison of distributed versus non-distributed training results.
- **Python libs:** TensorFlow, Horovod, Pandas, NumPy, scikit-learn
- **Is it Free?** Yes, all libraries and the UNSW-NB15 dataset are publicly available.
- **Relevant tool (Horovod) related Resource Links:** 
  - [Horovod Tutorial](https://github.com/horovod/horovod/blob/master/docs/tutorials/tensorflow.md)
  - [UNSW-NB15 Dataset](https://research.unsw.edu.au/projects/unsw-nb15-dataset-2015)

