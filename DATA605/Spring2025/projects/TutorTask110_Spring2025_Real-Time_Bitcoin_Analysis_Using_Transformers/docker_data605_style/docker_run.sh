#!/bin/bash -e

REPO_NAME=umd_data605
IMAGE_NAME=umd_data605_template
FULL_IMAGE_NAME=$REPO_NAME/$IMAGE_NAME
CONTAINER_NAME=btc_streamlit_app

# Run the container with port 8501 mapped for Streamlit
docker run --rm -ti \
    --name $CONTAINER_NAME \
    -p 8501:8501 \
    -v $(pwd)/../:/data \
    $FULL_IMAGE_NAME