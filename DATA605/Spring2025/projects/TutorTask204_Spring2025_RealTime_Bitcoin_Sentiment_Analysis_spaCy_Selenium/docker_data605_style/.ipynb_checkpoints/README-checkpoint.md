# Real-Time Bitcoin Sentiment Analysis with spaCy and Selenium

## Project Overview and Goals

This project, **TutorTask204_Spring2025_RealTime_Bitcoin_Sentiment_Analysis_spaCy_Selenium**, is a real-time sentiment analysis pipeline focused on Bitcoin-related tweets. It scrapes tweets using Selenium, preprocesses them with spaCy, analyzes sentiment with VADER, correlates sentiment with Bitcoin prices from CoinGecko, and visualizes the results. The project was developed as part of the DATA605 course in Spring 2025.

### Goals
- **Data Collection**: Scrape tweets containing keywords "Bitcoin" and "BTC" to capture public sentiment.
- **Sentiment Analysis**: Analyze tweet sentiment using VADER and categorize tweets as positive, negative, or neutral.
- **Correlation Analysis**: Compute multiple correlation measures (Pearson, Spearman, Kendall, and lagged Pearson) between sentiment scores and Bitcoin prices.
- **Visualization**: Generate insightful visualizations, including:
  - Line plot of sentiment vs. Bitcoin price over time.
  - Box plot of sentiment distribution.
  - Area plot of cumulative sentiment vs. Bitcoin price.
  - Correlation heatmap of sentiment, price, and other metrics.
  - Rolling correlation plot over time.
- **Usability**: Display visualizations directly in the Jupyter notebook for easy analysis.

## Project Structure

The project is organized within the `tutorials` repository under the `DATA605/Spring2025/projects` directory. Below is a diagram of the project structure:

TutorTask204_Spring2025_RealTime_Bitcoin_Sentiment_Analysis_spaCy_Selenium/
│
├── README.md                      # Project documentation and setup instructions
├── init.py                    # Makes the directory a Python package
├── main.py                        # Main script to run the pipeline
├── Bitcoin_API.md                 # Documentation for the sentiment analysis pipeline
├── Bitcoin_API.py                 # Core script for scraping, preprocessing, and visualization
├── Bitcoin_example.md             # Example usage of the sentiment analysis pipeline
├── Bitcoin_example.py             # Example script for single-tweet sentiment analysis
├── Bitcoin_utils.py               # Utility functions for logging
├── spacy_utils.py                 # Utility functions for NLP and CoinGecko API interactions
├── Bitcoin_Sentiment_Analysis.ipynb # Jupyter notebook demonstrating the pipeline
├── requirements.txt               # List of Python dependencies
├── Dockerfile                    # Docker configuration for the project
├── docker-compose.yml            # Docker Compose configuration for running the project
└── .gitignore                    # Specifies files and directories to ignore in Git


## How It Works

The pipeline operates in the following steps:

1. **Data Ingestion**:
   - Uses Selenium to scrape tweets from X (Twitter) for the keywords "Bitcoin" and "BTC".
   - Handles X login requirements with provided credentials, ensuring access to live search results.
   - Removes duplicate tweets based on text content.

2. **Data Preprocessing**:
   - Cleans tweets using spaCy for tokenization, stop-word removal, lemmatization, and Named Entity Recognition (NER).
   - Extracts entities and matches them with cryptocurrencies using CoinGecko data.

3. **Sentiment Analysis**:
   - Analyzes tweet sentiment using the VADER sentiment analyzer.
   - Categorizes tweets as positive, negative, or neutral based on compound scores.

4. **Correlation with Bitcoin Prices**:
   - Fetches Bitcoin price data from the CoinGecko API over a 1-day period.
   - Computes multiple correlation measures:
     - Pearson (linear relationship)
     - Spearman (monotonic relationship)
     - Kendall (rank-based)
     - Lagged Pearson (to explore if past sentiment predicts price)
     - Rolling correlation (to see how the relationship evolves over time)

5. **Visualizations**:
   - Generates plots displayed inline in the Jupyter notebook:
     - **Sentiment vs. Price Over Time**: A line plot showing sentiment scores and Bitcoin prices.
     - **Sentiment Distribution**: A box plot of sentiment scores across tweets.
     - **Cumulative Sentiment vs. Price**: An area plot comparing cumulative sentiment with price trends.
     - **Correlation Heatmap**: A heatmap of correlations between sentiment, price, price change, and rolling correlation.
     - **Rolling Correlation**: A line plot of the rolling correlation over time.

## Getting Started

### Prerequisites
- **Python 3.9+**: Ensure Python is installed on your system.
- **Google Chrome and ChromeDriver**: ChromeDriver must match your Chrome version for Selenium.
- **X (Twitter) Account**: Credentials are required for scraping tweets due to X's login requirements.
- **Docker and Docker Compose** (optional): For containerized execution.
- **Stable Internet Connection**: Needed for scraping tweets and fetching Bitcoin prices.

### Setup Instructions (Local Development)

1. Clone the Repository:
- git clone https://github.com/causify-ai/tutorials.git
- cd tutorials/DATA605/Spring2025/projects/TutorTask204_Spring2025_RealTime_Bitcoin_Sentiment_Analysis_spaCy_Selenium

2. Create and Activate a Virtual Environment (Windows):
- python -m venv venv
- venv\Scripts\activate

3. Create and Activate a Virtual Environment (macOS/Linux):
- python3 -m venv venv
- source venv/bin/activate

4. Install Dependencies:
- pip install -r requirements.txt

5. Install ChromeDriver:
- Download ChromeDriver matching your Chrome version from https://googlechromelabs.github.io/chromedriver/
- Place the chromedriver executable in the project directory or a directory in your PATH
- Update Bitcoin_Sentiment_Analysis.ipynb with the correct ChromeDriver path

6. Update X Credentials:
- Open Bitcoin_Sentiment_Analysis.ipynb
- Update the x_username and x_password fields in Cell 3 with your X credentials:
- x_username="your_username"
- x_password="your_password"
- Ensure 2FA is disabled for your X account, as Selenium cannot handle 2FA prompts automatically

7. Run the Jupyter Notebook Locally:
- jupyter notebook
- Open Bitcoin_Sentiment_Analysis.ipynb in your browser and run the cells to execute the pipeline