#!/bin/bash -e
#
# Execute a command in the container.
#

set -e
#set -x

CMD="$@"
echo "Executing: '$CMD'"

# Import the utility functions.
GIT_ROOT=$(git rev-parse --show-toplevel)
source $GIT_ROOT/docker_common/utils.sh

# Execute the script setting the vars for this tutorial.
get_docker_vars_script ${BASH_SOURCE[0]}
source $DOCKER_NAME
print_docker_vars

run "docker image ls $FULL_IMAGE_NAME"
#(docker manifest inspect $FULL_IMAGE_NAME | grep arch) || true

DOCKER_RUN_OPTS=""
CONTAINER_NAME=$IMAGE_NAME
run "docker run \
    --rm -ti \
    --name $CONTAINER_NAME \
    $DOCKER_RUN_OPTS \
    -v $(pwd):/data \
    $FULL_IMAGE_NAME \
    $CMD"
