#!/bin/bash

# Create necessary directories
mkdir -p /app/data/raw
mkdir -p /app/data/predictions
mkdir -p /app/data/predictions/history_data

# Set proper permissions
chmod -R 777 /app/data

# Wait for Kafka to be ready
echo "Waiting for Kafka to be ready..."
while ! nc -z kafka 29092; do
  sleep 1
done
echo "Kafka is ready!"

# Run the application
python /app/bitcoin_forecast_app/mains/run_instant.py 