#!/bin/bash -xe

REPO_NAME=umd_data605
IMAGE_NAME=document_search_engine
FULL_IMAGE_NAME=$IMAGE_NAME
CONTAINER_NAME=doc-search

docker image ls $FULL_IMAGE_NAME

# Run container with interactive bash shell
docker run -it \
    --name $CONTAINER_NAME \
    -p 8501:8501 \
    -p 11434:11434 \
    -v $(pwd):/app \
    $FULL_IMAGE_NAME /bin/bash