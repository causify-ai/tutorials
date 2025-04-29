#!/bin/bash

IMAGE_NAME="btc_snowflake_app"
CONTAINER_NAME="btc_container"

echo "Stopping and removing container: $CONTAINER_NAME"
docker stop $CONTAINER_NAME 2>/dev/null || echo "Container not running."
docker rm $CONTAINER_NAME 2>/dev/null || echo "Container does not exist."

echo "Removing image: $IMAGE_NAME"
docker rmi $IMAGE_NAME 2>/dev/null || echo "Image does not exist."

echo "Cleanup complete."
