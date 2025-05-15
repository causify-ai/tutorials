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

# Build container.
export DOCKER_BUILDKIT=1
#export DOCKER_BUILDKIT=0

#export DOCKER_BUILD_MULTI_ARCH=1
export DOCKER_BUILD_MULTI_ARCH=0
build_container_image
