#!/bin/bash
source ./docker_name.sh

echo "Executing into container: $CONTAINER_NAME"
docker exec -it $CONTAINER_NAME bash
