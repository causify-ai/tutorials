#!/bin/bash
#
# Build the Docker image for Bitcoin RDS with Streamlit
#

# Directory where this script is located
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd $DIR

# Source the docker name configuration
source ./docker_name.sh

# Set the image name for the Streamlit version
STREAMLIT_IMAGE_NAME="${IMAGE_NAME}_streamlit"
STREAMLIT_FULL_IMAGE_NAME="${REPO_NAME}/${STREAMLIT_IMAGE_NAME}"

echo "Building Bitcoin RDS Docker image with Streamlit: ${STREAMLIT_FULL_IMAGE_NAME}"

# Build the Docker image
docker build \
  -t ${STREAMLIT_FULL_IMAGE_NAME} \
  -f Dockerfile.streamlit \
  .

echo "Build complete. You can now run:"
echo "  ./docker_streamlit.sh   # For Streamlit dashboard" 