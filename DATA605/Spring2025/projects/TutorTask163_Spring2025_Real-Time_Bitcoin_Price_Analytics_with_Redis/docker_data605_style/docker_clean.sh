#!/bin/bash
# Script to clean up Docker resources related to Bitcoin analytics

# Stop any running containers
echo "Stopping running containers..."
docker stop bitcoin-analytics-container 2>/dev/null || true
docker stop bitcoin-analytics-container-bash 2>/dev/null || true

# Remove containers (should be automatic with --rm flag, but just in case)
echo "Removing containers if they exist..."
docker rm bitcoin-analytics-container 2>/dev/null || true
docker rm bitcoin-analytics-container-bash 2>/dev/null || true

# Optionally, remove the image (uncomment if needed)
# echo "Removing Docker image..."
# source ./docker_name.sh
# docker rmi "$DOCKER_NAME" 2>/dev/null || true

echo "Cleanup complete!"
