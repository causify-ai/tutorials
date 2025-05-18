#!/bin/bash -xe

CONTAINER_NAME=ollama-notebook
IMAGE_NAME=ollama-notebook

# Stop and remove container if running
if [ "$(docker ps -a -q -f name=$CONTAINER_NAME)" ]; then
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
fi

# Remove image if exists
if [ "$(docker images -q $IMAGE_NAME)" ]; then
    docker rmi $IMAGE_NAME
fi

# Show current containers and images
docker ps -a
docker images