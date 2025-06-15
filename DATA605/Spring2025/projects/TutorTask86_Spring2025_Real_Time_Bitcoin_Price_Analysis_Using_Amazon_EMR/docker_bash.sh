#!/bin/bash -xe

REPO_NAME=bitcoin_emr
IMAGE_NAME=bitcoin_emr_tutorial
FULL_IMAGE_NAME=$REPO_NAME/$IMAGE_NAME

docker image ls $FULL_IMAGE_NAME

CONTAINER_NAME=$IMAGE_NAME

docker run --rm -ti \
  --name $CONTAINER_NAME \
  -p 8888:8888 \
  $FULL_IMAGE_NAME




