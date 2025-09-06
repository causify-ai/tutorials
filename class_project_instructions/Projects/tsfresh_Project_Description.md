**Description**

In this project, students will utilize tsfresh, a Python package designed for time series feature extraction, to analyze and extract meaningful features from time series data. The tool automatically calculates a large number of time-series characteristics, making it easier for data scientists to prepare their data for machine learning tasks. 

Features:
- Automates the extraction of a wide range of time series features.
- Provides functionality to filter features based on relevance to the target variable.
- Supports multiple time series formats and can handle large datasets efficiently.

---

### Project 1: Time Series Classification of ECG Signals (Difficulty: 1)

**Project Objective**  
The goal is to classify different types of ECG signals (normal vs. abnormal) using time series data. Students will optimize the classification accuracy of the model.

**Dataset Suggestions**  
- **Dataset**: MIT-BIH Arrhythmia Database  
- **Source**: PhysioNet (https://physionet.org/static/published-project/gbm/)

**Tasks**  
- **Data Ingestion**: Load ECG signal data from the MIT-BIH database into a Pandas DataFrame.
- **Feature Extraction**: Use tsfresh to extract relevant time series features from the ECG signals.
- **Data Preprocessing**: Clean and prepare the extracted features for modeling.
- **Model Training**: Train a classification model (e.g., Random Forest) on the features to distinguish between normal and abnormal ECG signals.
- **Model Evaluation**: Evaluate the model using metrics such as accuracy, precision, and recall.

**Bonus Ideas (Optional)**  
- Explore different classification algorithms (e.g., SVM, Neural Networks) and compare their performance.
- Implement cross-validation to ensure robust model evaluation.

---

### Project 2: Predictive Maintenance of Industrial Machines (Difficulty: 2)

**Project Objective**  
The objective is to predict machine failures in an industrial setting based on sensor readings over time, optimizing for the accuracy of failure predictions.

**Dataset Suggestions**  
- **Dataset**: NASA Turbofan Engine Degradation Simulation Data Set  
- **Source**: NASA Prognostics Data Repository (https://www.nasa.gov/content/prognostics-center-of-excellence-data-set-repository)

**Tasks**  
- **Data Ingestion**: Load the sensor data from the NASA repository into a DataFrame.
- **Feature Extraction**: Utilize tsfresh to extract features from the time series data corresponding to different sensors.
- **Feature Selection**: Filter the extracted features based on their relevance to the target variable (failure occurrence).
- **Model Development**: Build a predictive model (e.g., Gradient Boosting) to forecast machine failures based on the selected features.
- **Model Evaluation**: Assess the model using confusion matrix and ROC-AUC score.

**Bonus Ideas (Optional)**  
- Investigate the impact of feature engineering techniques on model performance.
- Implement a real-time monitoring dashboard to visualize predictions.

---

### Project 3: Anomaly Detection in Network Traffic (Difficulty: 3)

**Project Objective**  
The goal is to detect anomalies in network traffic data, optimizing for the identification of potential security threats.

**Dataset Suggestions**  
- **Dataset**: UNSW-NB15 Dataset  
- **Source**: UNSW Cyber Security (https://www.unsw.adfa.edu.au/unsw-canberra-cyber/cybersecurity/unsw-nb15-dataset)

**Tasks**  
- **Data Ingestion**: Load the network traffic data into a DataFrame.
- **Feature Extraction**: Apply tsfresh to extract a comprehensive set of features from the time series data of network packets.
- **Anomaly Detection**: Utilize machine learning techniques (e.g., Isolation Forest, One-Class SVM) to identify anomalies in the extracted features.
- **Model Training and Evaluation**: Train the anomaly detection model and evaluate its performance using precision, recall, and F1 score.
- **Analysis of Anomalies**: Analyze detected anomalies to understand their characteristics and potential implications.

**Bonus Ideas (Optional)**  
- Create a visualization tool to display detected anomalies in real-time.
- Compare the performance of different anomaly detection algorithms on the dataset.

