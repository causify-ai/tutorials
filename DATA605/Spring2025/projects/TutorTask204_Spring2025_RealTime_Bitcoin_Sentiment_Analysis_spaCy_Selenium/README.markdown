# Real-Time Bitcoin Sentiment Analysis with spaCy and Selenium

## Overview
This project performs real-time sentiment analysis on Bitcoin-related tweets using Selenium for web scraping and spaCy for natural language processing (NLP). It analyzes the correlation between public sentiment and Bitcoin price movements using the VADER sentiment analyzer, with results demonstrated in a Jupyter notebook.

### Difficulty: 3 (Difficult)
The project involves web scraping, NLP, data analysis, and time-series visualization.

## Prerequisites
- Docker and Docker Compose installed on your machine.
- Python 3.9+ (if running without Docker).
- A compatible web browser (e.g., Chrome) for Selenium.

## Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Set Up the Docker Environment**:
   Build and run the Docker container:
   ```bash
   docker-compose up --build
   ```

3. **Install Dependencies** (if not using Docker):
   Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```

## Usage
1. **Run the Main Script** (optional, for standalone execution):
   ```bash
   python main.py
   ```
2. **Run the Jupyter Notebook** (to demonstrate the pipeline):
   - Start the Jupyter server in the Docker container (follow the URL provided, typically `http://localhost:8888`).
   - Open `Bitcoin_Sentiment_Analysis.ipynb` and run the cells sequentially.

## Project Structure
- `README.md`: Project overview and setup instructions.
- `__init__.py`: Makes the directory a Python package.
- `main.py`: Orchestrates the entire workflow for standalone execution.
- `spacy_utils.py`: Utility functions for NLP processing and CoinGecko API interactions.
- `Bitcoin_API.md`: Documentation for the sentiment analysis pipeline.
- `Bitcoin_API.py`: Core script for scraping, preprocessing, sentiment analysis, and correlation.
- `Bitcoin_example.md`: Example usage of the sentiment analysis pipeline.
- `Bitcoin_example.py`: Example script demonstrating sentiment analysis on a single tweet.
- `Bitcoin_utils.py`: Additional utility functions for logging.
- `Bitcoin_Sentiment_Analysis.ipynb`: Jupyter notebook demonstrating the pipeline.
- `requirements.txt`: List of Python dependencies.
- `Dockerfile`: Docker configuration for the project.
- `docker-compose.yml`: Docker Compose configuration for running the project.

## Technologies Used
- **spaCy**: For NLP tasks like tokenization and Named Entity Recognition (NER).
- **Selenium**: For scraping tweets from search queries.
- **VADER**: For sentiment analysis.
- **pandas**: For data manipulation and storage.
- **matplotlib**: For visualizing sentiment trends and price movements.
- **requests**: For fetching Bitcoin price data from CoinGecko API.

## Resources
- [spaCy Documentation](https://spacy.io/usage)
- [Selenium with Python Documentation](https://selenium-python.readthedocs.io/)
- [CoinGecko API Documentation](https://www.coingecko.com/en/api/documentation)
- [VADER Sentiment Documentation](https://github.com/cjhutto/vaderSentiment)