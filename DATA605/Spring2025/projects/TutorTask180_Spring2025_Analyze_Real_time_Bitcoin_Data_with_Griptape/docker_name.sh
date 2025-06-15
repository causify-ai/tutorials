# Set project root
GIT_ROOT=$(git rev-parse --show-toplevel)

# Optional: Load shared utils if you have them
if [ -f "$GIT_ROOT/docker_common/utils.sh" ]; then
    source "$GIT_ROOT/docker_common/utils.sh"
fi

# Define Docker image and container names for reuse
export IMAGE_NAME="griptape-bitcoin-project"
export CONTAINER_NAME="griptape-bitcoin-container"
