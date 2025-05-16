#!/bin/bash
# Script to get a bash shell in the running Docker container

set -e

# Check if the container is running
if docker ps | grep -q bitcoin-analytics-container; then
    echo "Connecting to running container..."
    docker exec -it bitcoin-analytics-container bash
else
    # If container is not running, start it with bash
    echo "Container not running. Starting new container with bash..."
    source ./docker_name.sh
    
    PARENT_DIR=$(dirname "$(pwd)")
    
    docker run --rm -it \
        -v "$PARENT_DIR":/home/jupyter/work \
        -v "$(pwd)/redis_data":/data/redis \
        --name bitcoin-analytics-container-bash \
        "$DOCKER_NAME" \
        bash
fi
