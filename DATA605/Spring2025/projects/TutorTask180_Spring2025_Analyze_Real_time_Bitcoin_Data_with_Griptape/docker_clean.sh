#!/bin/bash
source ./docker_name.sh

echo "Stopping container (if running)..."
docker stop $CONTAINER_NAME 2>/dev/null || true

echo "Removing container..."
docker rm $CONTAINER_NAME 2>/dev/null || true

echo "Removing image..."
docker rmi $IMAGE_NAME 2>/dev/null || true
