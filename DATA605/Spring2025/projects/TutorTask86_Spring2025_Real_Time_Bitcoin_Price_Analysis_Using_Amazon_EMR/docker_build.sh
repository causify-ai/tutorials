#!/bin/bash -e

REPO_NAME=bitcoin_emr
IMAGE_NAME=bitcoin_emr_tutorial

export DOCKER_BUILDKIT=1
docker build -t $REPO_NAME/$IMAGE_NAME .

