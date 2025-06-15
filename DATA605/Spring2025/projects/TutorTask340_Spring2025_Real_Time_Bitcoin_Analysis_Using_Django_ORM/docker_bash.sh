#!/bin/bash

REPO_NAME=umd_data605
IMAGE_NAME=umd_data605_template
FULL_IMAGE_NAME=$REPO_NAME/$IMAGE_NAME

CONTAINER_NAME=$IMAGE_NAME

# Run container and open a bash shell in /app
docker run --rm -ti \
    --name $CONTAINER_NAME \
    -p 8000:8000 \
    -v $(pwd):/app \
    -w /app \
    $FULL_IMAGE_NAME \
    bash
