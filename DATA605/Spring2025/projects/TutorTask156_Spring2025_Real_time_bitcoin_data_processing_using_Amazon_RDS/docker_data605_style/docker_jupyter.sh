#!/bin/bash
#
# Run Jupyter for Bitcoin RDS project
#

# Directory where this script is located
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd $DIR

# Source the docker name configuration
source ./docker_name.sh

# Default settings
JUPYTER_HOST_PORT=8888

# Calculate project directory (parent directory of the docker_data605_style folder)
PROJECT_DIR="$(cd .. && pwd)"

# Parse command line arguments for port
while getopts p: flag
do
    case "${flag}" in
        p) JUPYTER_HOST_PORT=${OPTARG};;
    esac
done

echo "Starting Jupyter notebook for Bitcoin RDS project..."
echo "Port: $JUPYTER_HOST_PORT"
echo "Project directory: $PROJECT_DIR"

# Run the Docker container
docker run \
    --rm -it \
    --name $IMAGE_NAME-jupyter \
    -p $JUPYTER_HOST_PORT:8888 \
    -v $PROJECT_DIR:/project \
    $FULL_IMAGE_NAME \
    jupyter notebook \
    --ip=0.0.0.0 \
    --port=8888 \
    --no-browser \
    --allow-root \
    --NotebookApp.notebook_dir=/project \
    --NotebookApp.token='' \
    --NotebookApp.password=''
