#!/bin/bash

IMAGE_NAME="faust-bitcoin-analysis"
CONTAINER_NAME="faust-bitcoin-dev"

echo "🐳 Running container $CONTAINER_NAME from image $IMAGE_NAME..."
docker run -it --rm \
  --name $CONTAINER_NAME \
  -p 8888:8888 \      # Jupyter
  -p 6066:6066 \      # Faust monitoring (if used)
  -v $(pwd):/app \    # Mount local project into container
  $IMAGE_NAME \
  /bin/bash
