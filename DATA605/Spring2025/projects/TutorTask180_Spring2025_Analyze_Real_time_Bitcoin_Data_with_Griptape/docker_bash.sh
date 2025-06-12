#!/bin/bash
source ./docker_name.sh

FULL_IMAGE_NAME=${FULL_IMAGE_NAME:-$IMAGE_NAME}
CONTAINER_PATH="/workspace"


echo "🔄 Running container from image: $FULL_IMAGE_NAME"
echo "📦 Container name: $CONTAINER_NAME"
echo "📁 Mounting local path: $HOST_PATH → $CONTAINER_PATH"

echo "docker run --rm -ti \
    --name \"$CONTAINER_NAME\" \
    -p 8888:8888 \
    -v $(pwd):/workspace/griptape \
    $FULL_IMAGE_NAME"

docker run --rm -ti \
    --name "$CONTAINER_NAME" \
    -p 8888:8888 \
    -v $(pwd):/workspace/griptape \
    $FULL_IMAGE_NAME
