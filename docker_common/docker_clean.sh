#!/bin/bash

set -e
#set -x

GIT_ROOT=$(git rev-parse --show-toplevel)
source $GIT_ROOT/docker_common/utils.sh

# Execute the script setting the vars for this tutorial.
get_docker_vars_script ${BASH_SOURCE[0]}
source $DOCKER_NAME
print_docker_vars

# Remove the container image.
remove_container_image
