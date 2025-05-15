#!/bin/bash -xe

REPO_NAME=umd_data605
IMAGE_NAME=umd_data605_template
FULL_IMAGE_NAME=document_search_engine

docker image ls $FULL_IMAGE_NAME

CONTAINER_NAME=doc-search
docker run -d \
    --name $CONTAINER_NAME \
    -p 8501:8501 \
    -p 11434:11434 \
    -v ${PWD}:/app \
    $FULL_IMAGE_NAME
