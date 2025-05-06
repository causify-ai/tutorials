#!/bin/bash
VERSION=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="docker_build.${VERSION}.log"
IMAGE_NAME="bitcoin_haystack:latest"
echo "🛠️  Building Docker image: $IMAGE_NAME"
echo "🗂️  Logging to: $LOG_FILE"
docker build -t $IMAGE_NAME . 2>&1 | tee "$LOG_FILE"
echo " Build complete. Log saved as $LOG_FILE"
