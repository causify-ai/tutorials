### Project 1: Weather Data Pipeline
- **Difficulty**: 1
- **Tech Description**: Use Airflow to orchestrate a simple ETL pipeline that fetches weather data from a public API and stores it in a database.
- **Project Idea**: The goal is to create a scheduled workflow that pulls daily weather data from the OpenWeatherMap API, transforms the data into a usable format, and loads it into a PostgreSQL database. The project will involve setting up Airflow to automate the data extraction, transformation, and loading processes. Students will learn to create tasks in Airflow, manage dependencies, and monitor pipeline execution.
- **Python libs**: requests, pandas, sqlalchemy, psycopg2
- **Is it Free?**: Yes, OpenWeatherMap offers a free tier for accessing weather data, and PostgreSQL is an open-source database.
- **Relevant tool (Airflow) related Resource Links**: 
  - [Airflow Documentation](https://airflow.apache.org/docs/)
  - [OpenWeatherMap API Documentation](https://openweathermap.org/api)

---

### Project 2: E-Commerce Sales Analysis Pipeline
- **Difficulty**: 2
- **Tech Description**: Utilize Airflow to build a data pipeline that extracts sales data from an e-commerce platform API, processes the data, and generates reports.
- **Project Idea**: This project aims to analyze sales data from the Shopify API to identify trends and generate weekly sales reports. Students will set up an Airflow DAG that pulls sales data, performs data cleaning and aggregation, and outputs the results to a CSV file. The project will emphasize data transformation, scheduling, and generating insights for business decisions.
- **Python libs**: requests, pandas, matplotlib, numpy
- **Is it Free?**: Yes, Shopify offers a free development store for testing, and the libraries used are open-source.
- **Relevant tool (Airflow) related Resource Links**: 
  - [Airflow DAG Tutorial](https://airflow.apache.org/docs/apache-airflow/stable/tutorial.html)
  - [Shopify API Documentation](https://shopify.dev/api)

---

### Project 3: Twitter Sentiment Analysis Workflow
- **Difficulty**: 3
- **Tech Description**: Implement an advanced Airflow pipeline to gather tweets, analyze sentiment using a pre-trained model, and visualize results.
- **Project Idea**: The objective is to create a complex workflow that extracts tweets related to a specific topic using the Twitter API, processes the text data, and applies a pre-trained sentiment analysis model (like VADER or TextBlob) to classify the sentiment of the tweets. The results will be stored in a database, and visualizations will be generated to display sentiment trends over time. This project will involve multiple tasks, including data extraction, analysis, and reporting, showcasing the power of Airflow in managing intricate workflows.
- **Python libs**: tweepy, pandas, nltk, matplotlib, sqlalchemy
- **Is it Free?**: Yes, the Twitter API has a free tier, and all libraries used are open-source.
- **Relevant tool (Airflow) related Resource Links**: 
  - [Airflow Best Practices](https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html)
  - [Twitter API Documentation](https://developer.twitter.com/en/docs/twitter-api)

