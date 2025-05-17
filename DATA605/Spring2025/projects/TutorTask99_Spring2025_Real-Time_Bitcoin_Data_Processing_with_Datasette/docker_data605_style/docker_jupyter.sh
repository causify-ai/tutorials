

#!/bin/bash
#
# Execute container that runs Jupyter and Datasette together.
#
# Usage:
# > ./docker_jupyter.sh -d /path/to/your/project -v -u -p 8888
#

set -e

# Parse params
export JUPYTER_HOST_PORT=8888
export JUPYTER_USE_VIM=0
export TARGET_DIR=""
export VERBOSE=0

OLD_CMD_OPTS=$@
while getopts p:d:uv flag; do
    case "${flag}" in
        p) JUPYTER_HOST_PORT=${OPTARG};;
        u) JUPYTER_USE_VIM=1;;
        d) TARGET_DIR=${OPTARG};;
        v) VERBOSE=1;;
    esac
done

if [[ $VERBOSE == 1 ]]; then
    set -x
fi

# Import utility functions
GIT_ROOT=$(git rev-parse --show-toplevel)
source $GIT_ROOT/docker_common/utils.sh

# Set Docker variables
get_docker_vars_script ${BASH_SOURCE[0]}
source $DOCKER_NAME
print_docker_vars

# Docker run options (expose both Jupyter and Datasette ports)
DOCKER_RUN_OPTS="-p $JUPYTER_HOST_PORT:$JUPYTER_HOST_PORT -p 8001:8001"
if [[ $TARGET_DIR != "" ]]; then
    DOCKER_RUN_OPTS="$DOCKER_RUN_OPTS -v $TARGET_DIR:/data"
fi

# Run the container using the default CMD from Dockerfile (/run_services.sh)
CONTAINER_NAME=$IMAGE_NAME
run "docker image ls $FULL_IMAGE_NAME"
(docker manifest inspect $FULL_IMAGE_NAME | grep arch) || true

run "docker run \
    --rm -ti \
    --name $CONTAINER_NAME \
    $DOCKER_RUN_OPTS \
    -v $(dirname $(pwd)):/curr_dir \
    -w /curr_dir \
    $FULL_IMAGE_NAME"
