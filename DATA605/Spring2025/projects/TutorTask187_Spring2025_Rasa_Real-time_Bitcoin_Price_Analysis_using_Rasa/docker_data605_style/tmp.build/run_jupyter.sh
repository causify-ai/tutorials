#!/bin/bash -xe

REPO_NAME=umd_data605
IMAGE_NAME=umd_data605_template
FULL_IMAGE_NAME=$REPO_NAME/$IMAGE_NAME

docker run --rm -ti \
    --name ${IMAGE_NAME}_jupyter \
    -p 8888:8888 \
    -v $(pwd):/data \
    $FULL_IMAGE_NAME \
    jupyter-notebook \
        --port=8888 \
        --no-browser --ip=0.0.0.0 \
        --allow-root \
        --NotebookApp.token='' \
        --NotebookApp.password=''
