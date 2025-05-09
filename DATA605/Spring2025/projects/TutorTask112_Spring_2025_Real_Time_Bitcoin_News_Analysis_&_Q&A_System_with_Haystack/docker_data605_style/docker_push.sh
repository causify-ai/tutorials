#!/bin/bash
IMAGE_NAME=bitcoin_haystack:latest
REMOTE_REPO=your_dockerhub_username/bitcoin_haystack

docker tag $IMAGE_NAME $REMOTE_REPO
docker push $REMOTE_REPO
