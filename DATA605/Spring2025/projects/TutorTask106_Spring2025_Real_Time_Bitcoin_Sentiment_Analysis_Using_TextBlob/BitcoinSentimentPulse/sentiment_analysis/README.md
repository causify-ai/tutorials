# Bitcoin Sentiment Analysis

This project analyzes sentiment from Bitcoin-related news articles using the NewsAPI and TextBlob for sentiment analysis. The results are stored in a PostgreSQL database and backed up to CSV files.

## Features

- Fetches Bitcoin-related news articles from NewsAPI
- Performs sentiment analysis using TextBlob
- Stores articles and sentiment analysis in PostgreSQL database
- Maintains daily aggregate sentiment statistics
- Provides CSV backup of sentiment data
- Docker support for easy deployment

## Prerequisites

- Python 3.9+
- PostgreSQL database
- NewsAPI key
- Docker (optional)

## Environment Variables

- `NEWS_API_KEY`: Your NewsAPI key
- `DATABASE_URL`: PostgreSQL connection URL (e.g., `postgresql://user:password@host:port/dbname`)
- `LOG_LEVEL`: Logging level (default: INFO)
- `LOG_FILE`: Path to log file (default: /var/log/sentiment_analysis/sentiment_analysis.log)

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables
4. Run the analyzer:
   ```bash
   python sentiment_analyzer.py
   ```

## Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t bitcoin-sentiment .
   ```

2. Run the container:
   ```bash
   docker run -d \
     -e NEWS_API_KEY=your_api_key \
     -e DATABASE_URL=your_db_url \
     bitcoin-sentiment
   ```

## Project Structure

- `sentiment_analyzer.py`: Main sentiment analysis implementation
- `logging_config.py`: Logging configuration
- `entrypoint.sh`: Container entrypoint script
- `requirements.txt`: Python dependencies
- `setup_requirements.txt`: Setup dependencies
- `Dockerfile`: Docker configuration

## Database Schema

### news_articles
- id (SERIAL PRIMARY KEY)
- article_id (TEXT UNIQUE)
- source (TEXT)
- author (TEXT)
- title (TEXT)
- description (TEXT)
- url (TEXT)
- published_at (TIMESTAMP)
- content (TEXT)
- created_at (TIMESTAMP)

### sentiment_analysis
- id (SERIAL PRIMARY KEY)
- article_id (TEXT REFERENCES news_articles)
- polarity (FLOAT)
- subjectivity (FLOAT)
- sentiment_category (TEXT)
- created_at (TIMESTAMP)

### aggregate_sentiment
- id (SERIAL PRIMARY KEY)
- date (DATE UNIQUE)
- avg_polarity (FLOAT)
- avg_subjectivity (FLOAT)
- positive_count (INTEGER)
- negative_count (INTEGER)
- neutral_count (INTEGER)
- article_count (INTEGER)
- created_at (TIMESTAMP)

## License

MIT License 