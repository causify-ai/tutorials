#!/bin/bash -xe

# Set project-specific names
REPO_NAME=tutortask123
IMAGE_NAME=btc_trade_huey_pipeline

# Full Docker image name
FULL_IMAGE_NAME=$REPO_NAME/$IMAGE_NAME

# Show images
docker image ls $FULL_IMAGE_NAME

# Run the container
docker run --rm -ti \
    --name $IMAGE_NAME \
    -p 8888:8888 \
    -v $(pwd)/..:/app \
    $FULL_IMAGE_NAME /bin/bash
