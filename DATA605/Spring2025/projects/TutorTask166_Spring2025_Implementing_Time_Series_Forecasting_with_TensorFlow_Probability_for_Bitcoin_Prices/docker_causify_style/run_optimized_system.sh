#!/bin/bash
# Script to run the Bitcoin forecasting system with optimal settings

set -e

echo "Starting Bitcoin Forecasting System with optimal settings..."

# Set environment variables for better performance
export TF_CPP_MIN_LOG_LEVEL=2  # Reduce TensorFlow logging
export PYTHONHASHSEED=0  # For reproducibility
export TF_FORCE_GPU_ALLOW_GROWTH=true  # Prevent TensorFlow from allocating all GPU memory

# Ensure directories exist
mkdir -p data/raw
mkdir -p data/predictions
mkdir -p data/backup

# Stop any running containers
echo "Stopping any running containers..."
docker-compose down

# Prune unused Docker resources to free up space
echo "Cleaning up Docker resources..."
docker system prune -f

# Rebuild containers
echo "Building containers with fresh dependencies..."
docker-compose build --no-cache

# Start the system
echo "Starting the system..."
docker-compose up -d

# Show logs for monitoring
echo "System started! Monitoring logs..."
docker-compose logs -f data-collector bitcoin-forecast-app dashboard

# To stop, press Ctrl+C and then run:
# docker-compose down 