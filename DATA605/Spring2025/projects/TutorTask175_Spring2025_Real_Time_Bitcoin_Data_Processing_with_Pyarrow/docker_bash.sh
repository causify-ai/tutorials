#!/bin/bash
source ./docker_name.sh

# Optional: if you define FULL_IMAGE_NAME in docker_name.sh, otherwise fallback to IMAGE_NAME
FULL_IMAGE_NAME=${FULL_IMAGE_NAME:-$IMAGE_NAME}

echo "Running a new container from image: $FULL_IMAGE_NAME"
echo "Container name: $CONTAINER_NAME"
echo "Current working directory: $(pwd)"
echo "docker run --rm -ti \
    --name $CONTAINER_NAME \
    -p 8888:8888 \
    -v $(pwd):/data \
    $FULL_IMAGE_NAME"

# docker run --rm -ti \
#   --name $CONTAINER_NAME \
#   -p 8888:8888 \
#   -v "/c/Users/varsh/OneDrive/Documents/grad school/tutorials1/DATA605/Spring2025/projects/TutorTask175_Spring2025_Real_Time_Bitcoin_Data_Processing_with_Pyarrow/docker_data605_style:/data" \
#   pyarrow-btc

docker run --rm -ti \
    --name $CONTAINER_NAME \
    -p 8888:8888 \
    -v $(pwd):/data \
    $FULL_IMAGE_NAME
