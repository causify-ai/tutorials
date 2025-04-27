#!/bin/bash -e

# Set project-specific names
REPO_NAME=tutortask123
IMAGE_NAME=btc_trade_huey_pipeline
FULL_IMAGE_NAME=$REPO_NAME/$IMAGE_NAME

# Push the image to Docker Hub
docker push $FULL_IMAGE_NAME
