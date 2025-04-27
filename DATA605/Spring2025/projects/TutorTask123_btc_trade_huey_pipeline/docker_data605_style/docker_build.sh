#!/bin/bash -e

# Set project-specific names
REPO_NAME=tutortask123
IMAGE_NAME=btc_trade_huey_pipeline

# Enable Docker BuildKit
export DOCKER_BUILDKIT=1

# Build Docker image
docker build -t $REPO_NAME/$IMAGE_NAME .
