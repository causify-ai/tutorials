#!/bin/bash -xe

CONTAINER_NAME=doc-search

# Check if container exists and stop it
if [ "$(docker ps -a -q -f name=$CONTAINER_NAME)" ]; then
    echo "Stopping and removing container $CONTAINER_NAME..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
    echo "Container stopped and removed."
else
    echo "Container $CONTAINER_NAME not found."
fi

# List running containers
echo "Running containers:"
docker ps 