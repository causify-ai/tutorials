# Set project root
GIT_ROOT=$(git rev-parse --show-toplevel)

# Define Docker image and container names for reuse
export IMAGE_NAME="presto-bitcoin-project"
export CONTAINER_NAME="presto-bitcoin-container"
