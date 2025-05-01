# 📊 Real-time Bitcoin Data Analysis using Twitter and spaCy

This project performs real-time sentiment monitoring on Bitcoin using scraped Twitter content, natural language processing via spaCy, and live price data from CoinGecko. It's built following the `DATA605` directory and Docker style to enable reproducible and modular data analysis.

## 1. `data605_style` (Simple Docker Environment)

- This version is modeled after the setup used in DATA605 tutorials
- This template provides a ready-to-run environment, including scripts to build,
  run, and clean the Docker container.

- For your specific project, you should:
  - Modify the Dockerfile to add project-specific dependencies
  - Update bash/scripts accordingly
  - Expose additional ports if your project requires them

## 2. `causify_style` (Causify AI dev-system)

- This project does not employ the causify_style.

## 🛠️ Technologies Used

### 🔹 spaCy
- A powerful, open-source NLP library designed for efficient and scalable text processing.  
- Provides functionalities such as **tokenization**, **part-of-speech tagging**, **named entity recognition (NER)**, and more.  
- Supports integration with deep learning frameworks like **TensorFlow** and **PyTorch**.

### 🔹 Selenium
- A **browser automation tool** that enables programmatic control of web browsers.  
- Useful for scraping **dynamic content** from websites that traditional tools like BeautifulSoup may not handle well.  

---

## 📂 Project Workflow

### 🔸 Objective:
To develop a system that:
- Scrapes **real-time Bitcoin-related tweets** using Selenium  
- Processes the text with **spaCy**  
- Analyzes and visualizes **public sentiment vs Bitcoin price**  

---

### 🔸 Steps:

#### ✅ 1. Data Ingestion
- Use Selenium to automate scraping of real-time tweets containing Bitcoin-related keywords (e.g., "Bitcoin", "BTC").
- Implement scraping based on the [selenium-twitter-scraper](https://github.com/StanGirard/selenium-twitter-scraper) GitHub repository.
- No Twitter API required.

#### ✅ 2. Data Preprocessing
- Clean and preprocess tweets using **spaCy**:
  - Tokenization
  - Stop-word removal
  - Lemmatization
- Perform **Named Entity Recognition (NER)** to extract mentions of cryptocurrencies and related topics.

#### ✅ 3. Sentiment Analysis
- Integrate sentiment tools like **VADER** or **TextBlob** with spaCy to score sentiment.
- Classify tweets as **positive**, **negative**, or **neutral**.

#### ✅ 4. Correlation with Bitcoin Price
- Fetch real-time Bitcoin price data using **CoinGecko API**.
- Store both sentiment scores and pricing data in **pandas DataFrames**.
- Conduct **time series analysis** to identify correlation trends.

#### ✅ 5. Visualization
- Use **matplotlib** or **seaborn** to create:
  - Line plots
  - Scatter plots  
- Display sentiment evolution alongside Bitcoin price changes.

---

## 📚 Resources

- [spaCy Documentation](https://spacy.io/)
- [Selenium with Python Docs](https://selenium-python.readthedocs.io/)
- [selenium-twitter-scraper GitHub](https://github.com/StanGirard/selenium-twitter-scraper)
- [CoinGecko API](https://www.coingecko.com/en/api/documentation)