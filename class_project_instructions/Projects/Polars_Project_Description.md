**Description**

Polars is a fast DataFrame library implemented in Rust, designed for high-performance data manipulation and analysis. Its features include:

- **Speed**: Optimized for performance with parallel execution and efficient memory usage.
- **Lazy Evaluation**: Supports lazy queries that allow you to build query plans and execute them only when needed.
- **Familiar API**: Offers a user-friendly API similar to pandas, making it easy for users to transition.
- **Integration**: Seamlessly integrates with various data sources, including CSV, Parquet, and JSON.

---

**Project 1: Customer Segmentation in Retail**  
**Difficulty**: 1 (Easy)

**Project Objective**: The goal is to segment customers based on their purchasing behavior using clustering techniques, optimizing for distinct customer profiles.

**Dataset Suggestions**: Look for retail transaction datasets on Kaggle or open government portals containing customer purchase history.

**Tasks**:
- **Data Ingestion**: Load the retail transaction dataset into a Polars DataFrame.
- **Data Cleaning**: Handle missing values and outliers in the dataset.
- **Feature Engineering**: Create features such as total spend, frequency of purchases, and product categories.
- **Clustering**: Implement K-means clustering to segment customers based on engineered features.
- **Visualization**: Use Polars to visualize the clusters and their characteristics for better insights.

**Bonus Ideas (Optional)**: Try using different clustering algorithms (e.g., DBSCAN) or compare the results with a classification model to predict customer segments.

---

**Project 2: Time Series Analysis of Air Quality Data**  
**Difficulty**: 2 (Medium)

**Project Objective**: Analyze air quality data to predict future pollution levels, optimizing for accuracy in predictions.

**Dataset Suggestions**: Utilize open datasets related to air quality from government APIs or Kaggle that provide historical pollution measurements.

**Tasks**:
- **Data Acquisition**: Load the air quality dataset into a Polars DataFrame, ensuring proper date-time parsing.
- **Data Resampling**: Resample the data to daily averages or other intervals to smoothen fluctuations.
- **Feature Engineering**: Create lag features and rolling averages to enhance predictive power.
- **Model Building**: Use regression techniques (e.g., ARIMA or Random Forest) to predict future pollution levels.
- **Evaluation**: Assess model performance using metrics like RMSE and visualize predictions against actual values.

**Bonus Ideas (Optional)**: Explore seasonal decomposition of time series or implement a more complex model like LSTM for improved predictions.

---

**Project 3: Movie Recommendation System**  
**Difficulty**: 3 (Hard)

**Project Objective**: Build a movie recommendation system using collaborative filtering and content-based filtering, optimizing for user satisfaction and diversity in recommendations.

**Dataset Suggestions**: Access movie ratings datasets on Kaggle or the MovieLens dataset available on open data repositories.

**Tasks**:
- **Data Loading**: Import the movie ratings and metadata into Polars DataFrames.
- **Data Preprocessing**: Clean the dataset by handling duplicates and missing values.
- **Feature Engineering**: Create a user-item interaction matrix and compute item similarities based on metadata (genres, directors).
- **Model Implementation**: Implement collaborative filtering using matrix factorization and combine it with content-based filtering.
- **Evaluation**: Use metrics such as precision, recall, and F1-score to evaluate the recommendation quality and visualize the results.

**Bonus Ideas (Optional)**: Enhance the recommendation system with additional features like user demographics or temporal dynamics, and compare performance against a baseline model.

