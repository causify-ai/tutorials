#!/bin/bash

# Name or ID of the container (use 'docker ps' to find this if needed)
CONTAINER_NAME="faust-bitcoin-container"

echo "🔍 Attaching to container: $CONTAINER_NAME"
docker exec -it $CONTAINER_NAME /bin/bash
