#!/bin/bash

# ✅ Match image and container name with build script
IMAGE_NAME=tutor_task114_s3fs_project
CONTAINER_NAME=tutor_task114_s3fs_container

# ✅ Jupyter port
JUPYTER_HOST_PORT=8888

# ✅ Optional AWS credentials mount
AWS_CREDENTIALS="$HOME/.aws"

echo "🚀 Launching Jupyter Lab from Docker container..."

docker run -it --rm \
    -p $JUPYTER_HOST_PORT:8888 \
    -v $(pwd):/app \
    -v $AWS_CREDENTIALS:/root/.aws \
    --name $CONTAINER_NAME \
    $IMAGE_NAME
