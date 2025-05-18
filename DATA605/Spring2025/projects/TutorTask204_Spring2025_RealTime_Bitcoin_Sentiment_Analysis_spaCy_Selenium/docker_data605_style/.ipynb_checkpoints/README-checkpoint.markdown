# Real-Time Bitcoin Sentiment Analysis with spaCy and Selenium

**Author**: Siddhi Rohan  
**UID**: 121302823  
**Course**: DATA605 — Spring 2025   

## Project Overview and Goals

This project, **TutorTask204_Spring2025_RealTime_Bitcoin_Sentiment_Analysis_spaCy_Selenium**, is a real-time sentiment analysis pipeline focused on Bitcoin-related tweets from X (Twitter). It leverages Selenium for web scraping, spaCy for natural language processing, VADER for sentiment analysis, and the CoinGecko API for Bitcoin price data, with results visualized in Jupyter notebooks. Developed for the DATA605 course in Spring 2025, the pipeline analyzes public sentiment and its correlation with Bitcoin price trends.

### Goals
- **Data Collection**: Scrape tweets containing keywords "Bitcoin" and "BTC" to capture public sentiment.
- **Sentiment Analysis**: Use VADER to analyze tweet sentiment, categorizing tweets as positive, negative, or neutral.
- **Correlation Analysis**: Compute multiple correlation measures (Pearson, Spearman, Kendall, lagged Pearson, and rolling) between sentiment scores and Bitcoin prices.
- **Visualization**: Generate insightful visualizations, including:
  - Line plot of sentiment vs. Bitcoin price over time.
  - Box plot of sentiment distribution.
  - Area plot of cumulative sentiment vs. Bitcoin price.
  - Correlation heatmap of sentiment, price, price change, and rolling correlation.
  - Rolling correlation plot over time.
- **Usability**: Display visualizations inline in Jupyter notebooks for easy analysis and exploration.

## Project Structure

The project is organized within the `tutorials` repository under the `DATA605/Spring2025/projects` directory. Below is the project structure:

```
TutorTask204_Spring2025_RealTime_Bitcoin_Sentiment_Analysis_spaCy_Selenium/
│
├── README.md                      # Project documentation and setup instructions
├── spacy_selenium_API.md          # Documentation for the sentiment analysis pipeline
├── spacy_selenium_example.md      # Example usage of the sentiment analysis pipeline
├── spacy_selenium_utils.py        # Core class for scraping, NLP, sentiment analysis, and visualization
├── spacy_selenium_API.ipynb       # Tutorial notebook demonstrating spaCy and Selenium APIs
├── spacy_selenium_example.ipynb   # End-to-end pipeline notebook
├── requirements.txt               # List of Python dependencies
├── Dockerfile                     # Docker configuration for the project
├── .gitignore                     # Specifies files and directories to ignore in Git
├── docker_build.sh                # Builds the Docker container             
├── docker_bash.sh                 # Launches Jupyter notebook server
├── install_project_packages.sh    # Installs pip dependencies inside the container
└── bashrc, etc_sudoers, utils.sh  # Helper configurations
```

## How It Works

The pipeline operates in the following steps:

1. **Data Ingestion**:
   - Uses Selenium to scrape tweets from X for keywords "Bitcoin" and "BTC".
   - Handles X login requirements with provided credentials to access live search results.
   - Removes duplicate tweets based on text content.

2. **Data Preprocessing**:
   - Cleans tweets using spaCy for tokenization, stop-word removal, lemmatization, and Named Entity Recognition (NER).
   - Matches extracted entities with cryptocurrencies using CoinGecko data.

3. **Sentiment Analysis**:
   - Analyzes tweet sentiment using the VADER sentiment analyzer.
   - Categorizes tweets as positive, negative, or neutral based on compound scores.

4. **Correlation with Bitcoin Prices**:
   - Fetches Bitcoin price data from the CoinGecko API over a 1-day period.
   - Computes multiple correlation measures:
     - **Pearson**: Linear relationship.
     - **Spearman**: Monotonic relationship.
     - **Kendall**: Rank-based correlation.
     - **Lagged Pearson**: Explores if past sentiment predicts price.

5. **Visualizations**:
   - Generates inline plots in Jupyter notebooks:
     - **Sentiment vs. Price Over Time**: Line plot of sentiment scores and Bitcoin prices.
     - **Sentiment Distribution**: Box plot of sentiment score distribution.
     - **Cumulative Sentiment vs. Price**: Area plot comparing cumulative sentiment with price trends.
     - **Correlation Heatmap**: Heatmap of correlations between sentiment, price, price change, and rolling correlation.
     - **Rolling Correlation**: Line plot of rolling correlation over time.

## Getting Started

### Prerequisites
- **Python 3.9+**: Ensure Python is installed.
- **Google Chrome and ChromeDriver**: ChromeDriver must match your Chrome version for Selenium.
- **X (Twitter) Account**: Valid credentials (`x_username`, `x_password`) are required for scraping.
- **Docker and Docker Compose** (optional): For containerized execution.
- **Stable Internet Connection**: Required for scraping tweets and fetching price data.
- **(Optional) CoinGecko API Key**: For paid tier to avoid rate limits.

### Setup Instructions (Local Development)

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/causify-ai/tutorials.git
   cd tutorials/DATA605/Spring2025/projects/TutorTask204_Spring2025_RealTime_Bitcoin_Sentiment_Analysis_spaCy_Selenium
   ```

2. **Create and Activate a Virtual Environment (Windows)**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Create and Activate a Virtual Environment (macOS/Linux)**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Install ChromeDriver**:
   - Download ChromeDriver matching your Chrome version from [chromedriver.chromium.org](https://chromedriver.chromium.org/downloads).
   - Place `chromedriver` in the project directory or a directory in your `PATH`.
   - Update `spacy_selenium_example.ipynb` or `spacy_selenium_utils.py` with the correct ChromeDriver path if needed.

6. **Update X Credentials**:
   - Open `spacy_selenium_example.ipynb` or `Bitcoin_Sentiment_Analysis.ipynb`.
   - Update the `x_username` and `x_password` fields in the relevant cell:
     ```python
     x_username="your_username"
     x_password="your_password"
     ```
   - Ensure 2FA is disabled for your X account, as Selenium cannot handle 2FA prompts.

7. **(Optional) Set Up CoinGecko API Key**:
   - Create a `.env` file in the project root:
     ```ini
     COINGECKO_API_KEY=your_key_here
     ```

8. **Run the Jupyter Notebook Locally**:
   ```bash
   jupyter notebook
   ```
   - Open `spacy_selenium_example.ipynb` or `Bitcoin_Sentiment_Analysis.ipynb` in your browser and run the cells to execute the pipeline.

### Setup Instructions (Docker)
Some of the Docker-related scripts were adjusted as per the project requirements. (Dockerfile, docker_build.sh and docker_bash.sh)
1. **Install Docker Desktop** for your operating system.

2. **Build the Docker Image**:
   ```bash
   chmod +x docker_data605_style/docker_*.sh
   ./docker_data605_style/docker_build.sh
   ```

3. **Jupyter Notebook Server**:
   - Start the container:
     ```bash
     ./docker_data605_style/docker_bash.sh
     ```
   - The jupyter notebook server loads up for you to dive right into the project for easier and faster access.



## Usage

### Run the API Functionality Demo
```bash
jupyter notebook spacy_selenium_API.ipynb
```
This notebook demonstrates:
- **spaCy API**: Tokenization, lemmatization, NER, and dependency parsing.
- **Selenium API**: Scraping tweets from X with authenticated login.
- Integration with `spacy_selenium_utils.py` for preprocessing and analysis.

### Run the Full Pipeline
```bash
jupyter notebook spacy_selenium_example.ipynb
```
The pipeline:
- Scrapes tweets for "Bitcoin" and "BTC".
- Preprocesses tweets with spaCy.
- Analyzes sentiment with VADER.
- Fetches Bitcoin price data from CoinGecko.
- Computes correlations and generates visualizations.

### Explore Interactively
- Start with `spacy_selenium_API.ipynb` to understand the APIs.
- Run `spacy_selenium_example.ipynb` or `Bitcoin_Sentiment_Analysis.ipynb` for the full pipeline.
- Use **Restart & Run All** in JupyterLab for consistent results.

## Troubleshooting

- **X Login Failure**:
  - Verify `x_username` and `x_password` in `spacy_selenium_example.ipynb` or `spacy_selenium_utils.py`.
  - Disable 2FA on your X account.
  - Check for verification prompts (email/phone) and handle manually (screenshots saved as `*.png`).

- **Selenium TimeoutException**:
  - Ensure ChromeDriver matches your Chrome version.
  - Increase `WebDriverWait` timeouts in `spacy_selenium_utils.py` (e.g., from 15s to 30s).

- **CoinGecko API Rate Limits**:
  - Use a paid API key in `.env` if rate-limited.
  - Reduce `max_tweets` in `spacy_selenium_example.ipynb`.

- **Docker Port Issues**:
  - Confirm `-p 8888:8888` is included in Docker commands.
  - Ensure port 8888 is free on your host machine.

- **Visualization Issues**:
  - Add `%matplotlib inline` at the top of notebook cells.
  - Update `matplotlib`, `seaborn`, and `ipython`:
    ```bash
    pip install --upgrade matplotlib seaborn ipython
    ```

## References
- [spaCy Documentation](https://spacy.io/usage)
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [VADER Sentiment Analysis](https://github.com/cjhutto/vaderSentiment)
- [CoinGecko API Documentation](https://www.coingecko.com/en/api/documentation)
- [Matplotlib Documentation](https://matplotlib.org/stable/contents.html)
- [Seaborn Documentation](https://seaborn.pydata.org/)