#!/bin/bash -e

echo "Stopping Bitcoin Price Forecasting System"

# Stop all containers
docker-compose down

echo "All containers have been stopped"