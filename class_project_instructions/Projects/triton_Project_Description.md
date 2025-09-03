### Project 1: Predicting Housing Prices with Triton

- **Difficulty**: 1
- **Tech Description**: Triton is used to optimize and accelerate the inference of a pre-trained regression model for housing price prediction.
- **Project Idea**: The goal of this project is to predict housing prices based on various features such as location, size, and number of bedrooms. Students will utilize a pre-trained regression model and deploy it using Triton to handle multiple inference requests efficiently. The project will involve data preprocessing, setting up the Triton server, and evaluating the model's performance on a test dataset. The dataset will be sourced from the Kaggle Housing Prices dataset.
- **Python libs**: Triton Inference Server, Pandas, NumPy, Scikit-learn, Matplotlib
- **Is it Free?**: Yes, Triton is open-source and free to use, and the Kaggle dataset is publicly available.
- **Relevant tool (Triton) related Resource Links**: 
  - [Triton Inference Server Documentation](https://docs.nvidia.com/deeplearning/triton-inference-server/user_guide/index.html)
  - [Kaggle Housing Prices Dataset](https://www.kaggle.com/c/house-prices-advanced-regression-techniques)

---

### Project 2: Real-Time Sentiment Analysis of Tweets

- **Difficulty**: 2
- **Tech Description**: Triton is employed to serve a pre-trained NLP model for real-time sentiment analysis of tweets, allowing for efficient batch processing of incoming data.
- **Project Idea**: In this project, students will build a sentiment analysis tool that processes tweets in real-time to determine public sentiment on various topics. Using the Twitter API, they will collect tweets related to a specific hashtag or event. A pre-trained sentiment analysis model will be deployed with Triton to handle incoming tweet data and provide insights into sentiment trends over time. The project will also involve visualizing sentiment changes using time-series graphs.
- **Python libs**: Triton Inference Server, Tweepy, Transformers, Matplotlib, Seaborn
- **Is it Free?**: Yes, both Triton and the Twitter API for basic access are free, and the sentiment analysis model from Hugging Face is publicly available.
- **Relevant tool (Triton) related Resource Links**: 
  - [Triton Inference Server GitHub](https://github.com/triton-inference-server/server)
  - [Twitter API Documentation](https://developer.twitter.com/en/docs/twitter-api)

---

### Project 3: Anomaly Detection in Network Traffic

- **Difficulty**: 3
- **Tech Description**: Triton is utilized to serve an anomaly detection model that identifies unusual patterns in network traffic data, optimizing the inference process for large datasets.
- **Project Idea**: This project aims to detect anomalies in network traffic data, which can indicate potential security threats. Students will use a publicly available dataset such as the CICIDS 2017 dataset. They will implement a pre-trained anomaly detection model and deploy it with Triton to analyze network traffic in batches. The project will include data preprocessing, model evaluation, and visualization of detected anomalies, providing insights into network security.
- **Python libs**: Triton Inference Server, Pandas, NumPy, Scikit-learn, Matplotlib
- **Is it Free?**: Yes, Triton is open-source, and the CICIDS 2017 dataset is freely available for research purposes.
- **Relevant tool (Triton) related Resource Links**: 
  - [CICIDS 2017 Dataset](https://www.unb.ca/cic/datasets/malmem-2021.html)
  - [Triton Inference Server Overview](https://developer.nvidia.com/nvidia-triton-inference-server)

