#!/bin/bash -xe

REPO_NAME=umd_data605
IMAGE_NAME=umd_data605_template
FULL_IMAGE_NAME=$REPO_NAME/$IMAGE_NAME

docker image ls $FULL_IMAGE_NAME

CONTAINER_NAME=$IMAGE_NAME
docker run --rm -ti \
    --name $CONTAINER_NAME \
    --entrypoint /data \    
    -p 8888:8888 \
    -v $(pwd):/data \
    $FULL_IMAGE_NAME
