#!/bin/bash -xe

REPO_NAME=umd_data605
IMAGE_NAME=umd_data605_real_time_bitcoin_price_analysis_with_tensorflow
FULL_IMAGE_NAME=$REPO_NAME/$IMAGE_NAME

docker image ls $FULL_IMAGE_NAME

CONTAINER_NAME=$IMAGE_NAME

docker run --rm -ti \
  --name "$CONTAINER_NAME" \
  --entrypoint /bin/bash \
  -p 8888:8888 \
  -p 8501:8501 \
  -v "$(dirname "$(pwd)")":/data \
  "$FULL_IMAGE_NAME"

