#!/bin/bash -e

# Set repository and image names
REPO_NAME=bitcoin-forecast
IMAGE_NAME=bitcoin-forecast-app

echo "Building Docker images for Bitcoin Price Forecasting System"

# Build container with BuildKit enabled for better caching
export DOCKER_BUILDKIT=1

echo "Building main application image..."
docker build -t ${REPO_NAME}/${IMAGE_NAME} -f Dockerfile .

echo "Building sentiment analysis image..."
docker build -t ${REPO_NAME}/sentiment-analyzer -f sentiment_analysis/Dockerfile .

echo "Images built successfully:"
docker image ls | grep ${REPO_NAME}