#!/bin/bash
source ./docker_name.sh

DOCKERHUB_USER=your_dockerhub_username_here

echo "Tagging and pushing image to DockerHub: $DOCKERHUB_USER/$IMAGE_NAME"
docker tag $IMAGE_NAME $DOCKERHUB_USER/$IMAGE_NAME
docker push $DOCKERHUB_USER/$IMAGE_NAME
