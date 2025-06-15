#!/bin/bash
#
# Clean up Docker images for Bitcoin RDS project
#

# Directory where this script is located
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd $DIR

# Source the docker name configuration
source ./docker_name.sh

echo "Removing Docker image: $FULL_IMAGE_NAME"

# Remove the Docker image
docker rmi $FULL_IMAGE_NAME

echo "Clean complete."
