### Project 1: Anomaly Detection in Network Traffic
- **Difficulty**: 1
- **Tech Description**: Stumpy is used to compute the matrix profile, which helps identify anomalies in time series data by comparing subsequences.
- **Project Idea**: The goal of this project is to analyze network traffic data to detect unusual patterns that may indicate security breaches or anomalies. Using the publicly available CICIDS 2017 dataset, students will preprocess the network traffic logs and apply Stumpy to compute the matrix profile. By setting thresholds for the distance measures, students can identify anomalous traffic patterns and visualize these anomalies over time. The project will culminate in a report detailing the findings and potential implications for network security.
- **Python libs**: stumpy, pandas, numpy, matplotlib, seaborn
- **Is it Free?**: Yes, the CICIDS 2017 dataset is publicly available and free to use.
- **Relevant tool (stumpy) related Resource Links**: [Stumpy Documentation](https://stumpy.readthedocs.io/en/latest/), [CICIDS 2017 Dataset](https://www.unb.ca/cic/datasets/malmem-2021.html)

---

### Project 2: Time Series Forecasting for Energy Consumption
- **Difficulty**: 2
- **Tech Description**: Stumpy is utilized to analyze and forecast energy consumption patterns by leveraging matrix profile techniques for time series analysis.
- **Project Idea**: This project aims to forecast energy consumption for a city using historical energy usage data from the UCI Machine Learning Repository. Students will use Stumpy to compute the matrix profile of the time series data, helping to identify seasonal patterns and anomalies. The insights gained will be used to build a forecasting model using traditional time series methods like ARIMA or exponential smoothing. The project will evaluate the accuracy of the forecasts and discuss how they can aid in energy management strategies.
- **Python libs**: stumpy, pandas, statsmodels, matplotlib, scikit-learn
- **Is it Free?**: Yes, the UCI energy consumption dataset is freely available for academic use.
- **Relevant tool (stumpy) related Resource Links**: [Stumpy Documentation](https://stumpy.readthedocs.io/en/latest/), [UCI Energy Consumption Dataset](https://archive.ics.uci.edu/ml/datasets/Individual+household+electric+power+consumption)

---

### Project 3: Clustering Behavior Patterns in Retail Sales
- **Difficulty**: 3
- **Tech Description**: Stumpy is employed to compute the matrix profile, enabling the identification of similar behavior patterns in retail sales data for clustering purposes.
- **Project Idea**: This advanced project focuses on clustering customer purchase behavior using transaction data from the Kaggle Retail Data set. Students will preprocess the sales data to create time series representations for different products or categories. Using Stumpy to compute the matrix profile, they will identify similar purchase patterns among customers. The project will then apply clustering algorithms (such as DBSCAN or K-means) on the derived features to segment customers based on their purchasing behavior. The results will be analyzed to derive marketing strategies tailored to different customer segments.
- **Python libs**: stumpy, pandas, numpy, scikit-learn, matplotlib
- **Is it Free?**: Yes, the Kaggle Retail Data set is publicly accessible and free for use.
- **Relevant tool (stumpy) related Resource Links**: [Stumpy Documentation](https://stumpy.readthedocs.io/en/latest/), [Kaggle Retail Data Set](https://www.kaggle.com/datasets/irfanasrullah/retail-data-set)

