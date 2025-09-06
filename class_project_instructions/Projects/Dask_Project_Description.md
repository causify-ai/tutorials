**Description**

In this project, students will utilize Dask, a flexible parallel computing library for analytics, to handle large datasets efficiently. Dask enables users to scale their workflows from a single machine to a cluster, making it ideal for big data applications. Its key features include:

- **Parallel Computing**: Distributes computation across multiple cores or machines to speed up processing.
- **Dask Arrays and DataFrames**: Provides parallelized versions of NumPy arrays and Pandas DataFrames for handling large datasets.
- **Task Scheduling**: Uses a dynamic task scheduler to optimize execution and resource allocation.

---

### Project 1: Movie Ratings Analysis
**Difficulty**: 1 (Easy)

**Project Objective**: Analyze and predict movie ratings based on various features like genre, director, and cast, using the MovieLens dataset. The goal is to build a simple regression model to predict user ratings.

**Dataset Suggestions**: 
- MovieLens 100K dataset available on [Kaggle](https://www.kaggle.com/grouplens/movielens-100k).

**Tasks**:
- **Set Up Dask Environment**: Install Dask and create a Dask DataFrame from the MovieLens dataset.
- **Data Preprocessing**: Clean and preprocess the dataset, handling missing values and converting categorical variables into numerical ones.
- **Feature Engineering**: Create new features such as average ratings per genre and director.
- **Model Training**: Use Dask-ML to train a regression model (e.g., Linear Regression) to predict ratings.
- **Evaluation**: Evaluate model performance using metrics like RMSE and visualize predictions against actual ratings.

---

### Project 2: E-commerce Sales Forecasting
**Difficulty**: 2 (Medium)

**Project Objective**: Develop a sales forecasting model for an e-commerce platform using historical sales data. The aim is to predict future sales using time series analysis.

**Dataset Suggestions**: 
- Retail sales data from the [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/datasets/Online+Retail).

**Tasks**:
- **Load Large Dataset with Dask**: Import the dataset using Dask to handle the large size efficiently.
- **Data Cleaning**: Remove duplicates and handle missing values in the sales records.
- **Time Series Decomposition**: Decompose the time series data into trend, seasonality, and residual components using Dask.
- **Modeling**: Implement a time series forecasting model (e.g., ARIMA or Prophet) using Dask-ML for scalability.
- **Visualization**: Plot the historical sales data and forecasted sales to analyze trends and seasonality.

---

### Project 3: Twitter Sentiment Analysis on COVID-19
**Difficulty**: 3 (Hard)

**Project Objective**: Perform sentiment analysis on a large dataset of tweets related to COVID-19 to identify public sentiment trends over time. The goal is to classify tweets as positive, negative, or neutral.

**Dataset Suggestions**: 
- COVID-19 tweets dataset available on [Kaggle](https://www.kaggle.com/datasets/sbhatti/real-time-covid-19-tweets).

**Tasks**:
- **Ingest Large Dataset**: Load the Twitter dataset using Dask to manage the size and complexity of the data.
- **Text Preprocessing**: Clean the tweet text (removing URLs, mentions, and special characters) and tokenize the text using Dask's parallel processing capabilities.
- **Feature Extraction**: Use techniques like TF-IDF or word embeddings to convert text data into numerical features.
- **Sentiment Classification**: Train a machine learning model (e.g., Random Forest or XGBoost) using Dask-ML to classify sentiments.
- **Analysis of Results**: Analyze the results, visualize sentiment trends over time, and correlate them with significant COVID-19 events.

**Bonus Ideas (Optional)**:
- For Project 2, explore seasonal decomposition further by applying Fourier transforms to identify hidden patterns.
- For Project 3, consider using a pre-trained transformer model (like BERT) with Dask for improved sentiment classification performance.

