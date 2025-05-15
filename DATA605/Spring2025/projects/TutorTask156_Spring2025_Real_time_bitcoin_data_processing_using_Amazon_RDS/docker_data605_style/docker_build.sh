#!/bin/bash
#
# Build Docker image for Bitcoin RDS project
#

# Directory where this script is located
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd $DIR

# Source the docker name configuration
source ./docker_name.sh

echo "Building Bitcoin RDS Docker image: $FULL_IMAGE_NAME"

# Build Docker image with no cache
docker build -t $FULL_IMAGE_NAME .

echo "Build complete. You can now run:"
echo "  ./docker_jupyter.sh   # For Jupyter Notebook"
echo "  ./docker_bash.sh      # For bash shell"
