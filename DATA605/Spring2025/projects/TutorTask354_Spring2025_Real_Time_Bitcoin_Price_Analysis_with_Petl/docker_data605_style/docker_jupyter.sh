#!/usr/bin/env bash
REPO_NAME=umd_data605
IMAGE_NAME=umd_data605_template
FULL_IMAGE_NAME=${REPO_NAME}/${IMAGE_NAME}

docker run --rm -it \
  -v "$(pwd)":/home/jovyan/work \
  -p 8888:8888 \
  $FULL_IMAGE_NAME \
  jupyter notebook --ip=0.0.0.0 --allow-root --notebook-dir=/home/jovyan/work



