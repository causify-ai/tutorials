#!/bin/bash -e

cd "$(dirname "$0")"

GIT_ROOT=$(git rev-parse --show-toplevel)
source $GIT_ROOT/docker_common/utils.sh

REPO_NAME=umd_data605
IMAGE_NAME=bitcoin_cli_project

# Build container.
export DOCKER_BUILDKIT=1
#export DOCKER_BUILDKIT=0
BUILD_ARGS="$@"
build_container_image $BUILD_ARGS
