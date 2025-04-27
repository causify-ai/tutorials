#!/bin/bash -e

# Set project-specific names
REPO_NAME=tutortask123
IMAGE_NAME=btc_trade_huey_pipeline

# Expose Jupyter port
JUPYTER_PORT=8888

# Full image name
FULL_IMAGE_NAME=$REPO_NAME/$IMAGE_NAME

# Build and run the container
docker run --rm -ti \
    --name $IMAGE_NAME \
    -p $JUPYTER_PORT:8888 \
    -v $(pwd):/app \
    $FULL_IMAGE_NAME \
    jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root --NotebookApp.token=''
