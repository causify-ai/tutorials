#!/bin/bash
# Script to restart the Bitcoin forecasting system with optimized settings

set -e

echo "===== Bitcoin Forecasting System - Optimized Restart ====="

# Move to script directory
cd "$(dirname "$0")"

# Stop existing containers
echo "Stopping existing containers..."
docker-compose down

# Clean up Docker system
echo "Cleaning up Docker resources..."
docker system prune -f

# Clear any potentially corrupted prediction data (we'll keep the raw data)
echo "Backing up existing prediction data..."
BACKUP_DIR="./data/predictions/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR
cp -rf ./data/predictions/*.csv $BACKUP_DIR/ 2>/dev/null || true

echo "Clearing prediction files to start fresh..."
rm -f ./data/predictions/instant_predictions.csv
rm -f ./data/predictions/instant_metrics.csv

# Create fresh prediction files with headers
echo "Creating fresh prediction files..."
mkdir -p ./data/predictions
echo "timestamp,pred_price,pred_lower,pred_upper" > ./data/predictions/instant_predictions.csv
echo "timestamp,std,mae,rmse,actual_error" > ./data/predictions/instant_metrics.csv

# Ensure data directory exists for raw data
mkdir -p ./data/raw

# Limit the raw data file to last 10,000 lines to improve performance
echo "Trimming raw data file to last 10,000 lines..."
if [ -f "./data/raw/instant_data.csv" ]; then
    tail -10000 ./data/raw/instant_data.csv > ./data/raw/instant_data.tmp
    mv ./data/raw/instant_data.tmp ./data/raw/instant_data.csv
fi

# Rebuild the containers with the optimized settings
echo "Building containers with optimized settings..."
docker-compose build

# Start the system
echo "Starting containers..."
docker-compose up -d

# Wait for services to be healthy
echo "Waiting for services to be ready..."
sleep 10

# Monitor logs for successful initialization
echo "Checking logs for startup progress..."
docker-compose logs --tail=20 bitcoin-forecast-app

echo "===== System restarted with optimized settings ====="
echo "Monitor performance with: docker-compose logs -f bitcoin-forecast-app"
echo "View predictions at: http://localhost:8501" 