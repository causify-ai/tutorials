#!/bin/bash -xe

REPO_NAME=umd_data605
IMAGE_NAME=document_search_engine
FULL_IMAGE_NAME=$IMAGE_NAME
CONTAINER_NAME=doc-search

# Check if container already exists and remove it
if [ "$(docker ps -a -q -f name=$CONTAINER_NAME)" ]; then
    docker stop $CONTAINER_NAME || true
    docker rm $CONTAINER_NAME || true
fi

# Run container in detached mode (uses CMD from Dockerfile)
docker run -d \
    --name $CONTAINER_NAME \
    -p 8501:8501 \
    -p 11434:11434 \
    -v $(pwd):/app \
    $FULL_IMAGE_NAME

echo "Container started. Access the app at http://localhost:8501"
echo "To view logs, run: docker logs -f $CONTAINER_NAME" 