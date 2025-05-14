#!/bin/bash -e

# Define image and container names
IMAGE_NAME=btc_snowflake_app
CONTAINER_NAME=btc_container

echo "Building Docker image..."
docker build -t $IMAGE_NAME .

echo "Running Docker container with .env and volume mounts..."
docker run -it --rm \
  --env-file .env \
  -v "$(pwd)":/project \
  -p 8888:8888 \
  -p 8502:8502 \
  --name $CONTAINER_NAME \
  $IMAGE_NAME