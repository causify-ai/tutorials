#!/bin/bash
#
# Run bash shell in the Bitcoin RDS project container
#

# Directory where this script is located
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd $DIR

# Source the docker name configuration
source ./docker_name.sh

# Set the project directory
PROJECT_DIR=/home/yunlong/src/tutorials1/DATA605/Spring2025/projects/TutorTask156_Spring2025_Real_time_bitcoin_data_processing_using_Amazon_RDS

echo "Starting bash shell for Bitcoin RDS project..."
echo "Using image: $FULL_IMAGE_NAME"

# Run Docker container with bash shell
docker run --rm -it \
    --name $IMAGE_NAME-bash \
    -v $PROJECT_DIR:/project \
    $FULL_IMAGE_NAME \
    /bin/bash

