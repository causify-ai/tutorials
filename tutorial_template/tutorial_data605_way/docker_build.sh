#!/bin/bash -e

GIT_ROOT=$(git rev-parse --show-toplevel)
source $GIT_ROOT/tutorial_github_simple/docker_common/utils.sh

REPO_NAME=pmodi08
IMAGE_NAME=umd_data605_template

# Build container.
export DOCKER_BUILDKIT=1
#export DOCKER_BUILDKIT=0
build_container_image
