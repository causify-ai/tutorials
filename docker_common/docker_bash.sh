#!/bin/bash

set -e
#set -x

# Import the utility functions.
GIT_ROOT=$(git rev-parse --show-toplevel)
source $GIT_ROOT/docker_common/utils.sh

# Execute the script setting the vars for this tutorial.
get_docker_vars_script ${BASH_SOURCE[0]}
source $DOCKER_NAME
print_docker_vars

run "docker image ls $FULL_IMAGE_NAME"

CONTAINER_NAME=${IMAGE_NAME}_bash
PORT=8889
cmd="docker run --rm -ti \
    --name $CONTAINER_NAME \
    -p $PORT:$PORT \
    -v $(pwd):/data \
    $FULL_IMAGE_NAME"
run $cmd
