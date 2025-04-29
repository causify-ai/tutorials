#!/bin/bash -e

# Set image name
IMAGE_NAME="btc_snowflake_app"

# Build Docker image from Dockerfile
docker build -f docker_data605_style/Dockerfile -t $IMAGE_NAME .

echo "Docker image '$IMAGE_NAME' built successfully."
