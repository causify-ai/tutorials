#!/bin/bash -xe

REPO_NAME=umd_data605
IMAGE_NAME=ollama-notebook
FULL_IMAGE_NAME=$IMAGE_NAME

docker image ls $FULL_IMAGE_NAME

# Build container
export DOCKER_BUILDKIT=1
docker build -t $FULL_IMAGE_NAME -f ./docker_data605_style/Dockerfile .