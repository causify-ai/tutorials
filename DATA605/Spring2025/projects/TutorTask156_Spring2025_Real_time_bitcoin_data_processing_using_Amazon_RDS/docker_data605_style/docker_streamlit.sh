#!/bin/bash
#
# Run Streamlit dashboard for Bitcoin RDS project
#

# Directory where this script is located
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd $DIR

# Source the docker name configuration
source ./docker_name.sh

# Set the image name for the Streamlit version
STREAMLIT_IMAGE_NAME="${IMAGE_NAME}_streamlit"
STREAMLIT_FULL_IMAGE_NAME="${REPO_NAME}/${STREAMLIT_IMAGE_NAME}"

# Default settings
STREAMLIT_HOST_PORT=6666

# Calculate project directory (parent directory of the docker_data605_style folder)
PROJECT_DIR="$(cd .. && pwd)"

# Parse command line arguments for port
while getopts p: flag
do
    case "${flag}" in
        p) STREAMLIT_HOST_PORT=${OPTARG};;
    esac
done

echo "Starting Streamlit dashboard for Bitcoin RDS project..."
echo "Port: $STREAMLIT_HOST_PORT"
echo "Project directory: $PROJECT_DIR"

# Run the Docker container
docker run \
    --rm -it \
    --name $STREAMLIT_IMAGE_NAME-dashboard \
    -p $STREAMLIT_HOST_PORT:8501 \
    -v $PROJECT_DIR:/project \
    $STREAMLIT_FULL_IMAGE_NAME \
    /usr/local/bin/run_streamlit.sh 