#!/bin/bash -e

echo "Bitcoin Price Forecasting System - Database Initialization"
echo "This script will initialize the PostgreSQL database tables needed for sentiment analysis"

# Set default values for Docker environment
DB_NAME=${DB_NAME:-bitcoin_sentiment}
DB_USER=${DB_USER:-postgres}
DB_PASSWORD=${DB_PASSWORD:-postgres}
DB_HOST=${DB_HOST:-db}  # Changed from localhost to db (Docker service name)
DB_PORT=${DB_PORT:-5432}

# Function to check if PostgreSQL is running and ready
check_postgres() {
    echo "Waiting for PostgreSQL to be ready..."
    for i in {1..30}; do
        if pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; then
            return 0
        fi
        echo "Waiting for PostgreSQL... attempt $i of 30"
        sleep 2
    done
    return 1
}

# Function to create database and user
create_db_and_user() {
    # Create database if it doesn't exist
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -tc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1 || \
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "CREATE DATABASE $DB_NAME;"

    # Grant privileges
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
}

# Function to initialize database tables
init_tables() {
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME << EOF
    -- Create news articles table
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

    -- Create sentiment analysis table
    CREATE TABLE IF NOT EXISTS sentiment_analysis (
        id SERIAL PRIMARY KEY,
        article_id TEXT REFERENCES news_articles(article_id),
        polarity FLOAT,
        subjectivity FLOAT,
        sentiment_category TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Create aggregate sentiment table
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
}

# Main execution
echo "Checking PostgreSQL connection..."
if check_postgres; then
    echo "PostgreSQL is running and ready"
    
    echo "Creating database and user..."
    create_db_and_user
    
    echo "Initializing database tables..."
    init_tables
    
    echo "Database initialization completed successfully"
else
    echo "Error: PostgreSQL is not running or not ready on $DB_HOST:$DB_PORT"
    exit 1
fi

echo "You can now run the Bitcoin Price Forecasting System with Docker Compose."