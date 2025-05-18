#!/bin/bash

# Set up logging
LOG_DIR="/var/log/sentiment_analysis"
mkdir -p "$LOG_DIR"
export LOG_FILE="$LOG_DIR/sentiment_analysis.log"

# Set up data directory
DATA_DIR="${DATA_DIR:-data}"
mkdir -p "$DATA_DIR"
export DATA_DIR

# Check if PostgreSQL is ready
if [ -n "$DATABASE_URL" ]; then
    # Extract host and port from DATABASE_URL
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\).*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    
    echo "Waiting for PostgreSQL to be ready..."
    while ! nc -z "$DB_HOST" "$DB_PORT"; do
        sleep 1
    done
    echo "PostgreSQL is ready!"
    
    # Initialize database tables if they don't exist
    echo "Initializing database tables..."
    psql "$DATABASE_URL" << EOF
    CREATE TABLE IF NOT EXISTS news_articles (
        id SERIAL PRIMARY KEY,
        article_id TEXT UNIQUE,
        source TEXT,
        author TEXT,
        title TEXT,
        description TEXT,
        url TEXT,
        published_at TIMESTAMP,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS sentiment_analysis (
        id SERIAL PRIMARY KEY,
        article_id TEXT REFERENCES news_articles(article_id),
        polarity FLOAT,
        subjectivity FLOAT,
        sentiment_category TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS aggregate_sentiment (
        id SERIAL PRIMARY KEY,
        date DATE UNIQUE,
        avg_polarity FLOAT,
        avg_subjectivity FLOAT,
        positive_count INTEGER,
        negative_count INTEGER,
        neutral_count INTEGER,
        article_count INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
EOF
else
    echo "Warning: DATABASE_URL not set. Database functionality will be disabled."
fi

# Check for NEWS_API_KEY
if [ -z "$NEWS_API_KEY" ]; then
    echo "Warning: NEWS_API_KEY not set. News API functionality will be disabled."
fi

# Create CSV backup directory
CSV_DIR="$DATA_DIR/csv_backups"
mkdir -p "$CSV_DIR"

# Initialize backup file if it doesn't exist
BACKUP_FILE="$CSV_DIR/sentiment_data.csv"
if [ ! -f "$BACKUP_FILE" ]; then
    echo "date,avg_polarity,avg_subjectivity,positive_count,negative_count,neutral_count,article_count" > "$BACKUP_FILE"
fi

# Start the sentiment analysis service
echo "Starting sentiment analysis service..."
python sentiment_analyzer.py 