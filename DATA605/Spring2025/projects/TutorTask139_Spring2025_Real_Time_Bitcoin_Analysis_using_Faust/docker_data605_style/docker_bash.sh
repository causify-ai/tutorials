#!/bin/bash

IMAGE_NAME="faust-bitcoin-analysis"
CONTAINER_NAME="faust-bitcoin-dev"

echo "🐳 Running container $CONTAINER_NAME from image $IMAGE_NAME..."
docker run -it --rm \
  --name $CONTAINER_NAME \
  -p 8888:8888 \
  -p 6066:6066 \
  -v $(pwd):/app \
  $IMAGE_NAME \
  /bin/bash
