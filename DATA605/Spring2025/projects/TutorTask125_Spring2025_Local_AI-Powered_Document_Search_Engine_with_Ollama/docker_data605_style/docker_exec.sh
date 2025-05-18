#!/bin/bash -xe

CONTAINER_NAME=ollama-notebook

# Check if container is running
if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    docker exec -it $CONTAINER_NAME /bin/bash
else
    echo "Container $CONTAINER_NAME is not running"
    docker ps
fi