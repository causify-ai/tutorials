#!/bin/bash
set -e

# Load the Docker name configuration
source ./docker_name.sh

# Build the Docker image
echo "Building Docker image: $DOCKER_NAME"
docker build -t "$DOCKER_NAME" \
    --build-arg CACHEBUST=$(date +%s) \
    .

echo "Docker image built successfully!"
