#!/bin/bash

# ---------------------------
# Clean Docker container/image
# ---------------------------

CONTAINER_NAME=tutor_task114_s3fs_container
IMAGE_NAME=tutor_task114_s3fs_project

echo "🧼 Cleaning Docker container and image..."

# Stop and remove container (if it exists)
if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "🔻 Stopping and removing container: $CONTAINER_NAME"
    docker rm -f $CONTAINER_NAME
else
    echo "✅ No matching container found."
fi

# Remove image (if it exists)
if [ "$(docker images -q $IMAGE_NAME)" ]; then
    echo "🔻 Removing image: $IMAGE_NAME"
    docker rmi -f $IMAGE_NAME
else
    echo "✅ No matching image found."
fi
