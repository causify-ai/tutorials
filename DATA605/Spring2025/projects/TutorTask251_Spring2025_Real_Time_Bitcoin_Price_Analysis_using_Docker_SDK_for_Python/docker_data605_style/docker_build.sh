#!/bin/bash -e

GIT_ROOT=$(git rev-parse --show-toplevel)
source $GIT_ROOT/docker_common/utils.sh

REPO_NAME=bitcoin_realtime_sdk
IMAGE_NAME=bitcoin_realtime_sdk

# Build container.
export DOCKER_BUILDKIT=1
build_container_image
