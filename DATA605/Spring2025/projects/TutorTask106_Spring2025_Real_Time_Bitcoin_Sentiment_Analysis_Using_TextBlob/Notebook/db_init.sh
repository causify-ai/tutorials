#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Initializing PostgreSQL database..."

# Check if PostgreSQL image exists
if ! docker image inspect postgres:14 >/dev/null 2>&1; then
    echo "PostgreSQL image not found. Pulling postgres:14..."
    docker pull postgres:14
fi

# Check if container is running
if ! docker ps | grep -q "postgres-bitcoin"; then
    echo "Starting PostgreSQL container..."
    docker run --name postgres-bitcoin \
        -e POSTGRES_USER=postgres \
        -e POSTGRES_PASSWORD=postgres \
        -e POSTGRES_DB=bitcoin_forecast \
        -p 5432:5432 \
        -d postgres:14

    # Wait for PostgreSQL to be ready
    echo "Waiting for PostgreSQL to be ready..."
    sleep 10
fi

# Create tables
echo "Creating database tables..."
docker exec postgres-bitcoin psql -U postgres -d bitcoin_forecast -c "
CREATE TABLE IF NOT EXISTS news_articles (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    url TEXT UNIQUE,
    published_at TIMESTAMP,
    source TEXT,
    sentiment_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);"

docker exec postgres-bitcoin psql -U postgres -d bitcoin_forecast -c "
CREATE TABLE IF NOT EXISTS sentiment_analysis (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES news_articles(id),
    polarity FLOAT,
    subjectivity FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);"

docker exec postgres-bitcoin psql -U postgres -d bitcoin_forecast -c "
CREATE TABLE IF NOT EXISTS aggregate_sentiment (
    id SERIAL PRIMARY KEY,
    date DATE UNIQUE,
    avg_polarity FLOAT,
    avg_subjectivity FLOAT,
    positive_count INTEGER,
    negative_count INTEGER,
    neutral_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);"

echo -e "${GREEN}Database initialization completed successfully!${NC}"
echo "PostgreSQL is running on localhost:5432"
echo "Database: bitcoin_forecast"
echo "Username: postgres"
echo "Password: postgres" 