#!/bin/bash

REPO_NAME=umd_data605
IMAGE_NAME=umd_data605_template
FULL_IMAGE_NAME=$REPO_NAME/$IMAGE_NAME
CONTAINER_NAME=$IMAGE_NAME

# Default Jupyter port
JUPYTER_PORT=8888

# Run Jupyter Notebook inside Docker container
docker run --rm -ti \
    --name $CONTAINER_NAME \
    -p $JUPYTER_PORT:$JUPYTER_PORT \
    -v $(pwd):/app \
    -w /app \
    $FULL_IMAGE_NAME \
    jupyter notebook --ip=0.0.0.0 --port=$JUPYTER_PORT --no-browser --allow-root
