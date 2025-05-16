#!/bin/bash
# Script to run Jupyter in Docker container

set -e

# Load Docker name configuration
source ./docker_name.sh

# Create a directory for Redis data persistence if it doesn't exist
mkdir -p ./redis_data

# Current directory to mount in the container
CURRENT_DIR=$(pwd)
PARENT_DIR=$(dirname "$CURRENT_DIR")

# Run the Docker container
echo "Starting Docker container with Jupyter and Redis..."
docker run \
    --rm \
    -it \
    -p 8888:8888 \
    -p 6379:6379 \
    -v "$PARENT_DIR":/home/jupyter/work \
    -v "$CURRENT_DIR/redis_data":/data/redis \
    -e REDIS_HOST=localhost \
    -e REDIS_PORT=6379 \
    -e REDIS_PASSWORD="" \
    --name bitcoin-analytics-container \
    "$DOCKER_NAME"

# Instructions for accessing Jupyter
echo "
============================================================
Jupyter Lab is running at: http://localhost:8888
Redis is running on port 6379
============================================================
"
