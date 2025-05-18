#!/bin/bash -xe

REPO_NAME=bitcoin_realtime_sdk
IMAGE_NAME=bitcoin_realtime_sdk
FULL_IMAGE_NAME=$REPO_NAME

# List images for debugging

docker image ls $FULL_IMAGE_NAME

CONTAINER_NAME=$IMAGE_NAME
# Mount the project directory for live development
PROJECT_DIR=$(pwd)/..
docker run --rm -ti \
    --name $CONTAINER_NAME \
    -p 8888:8888 \
    -v $PROJECT_DIR:/data \
    $FULL_IMAGE_NAME
