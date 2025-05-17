#!/bin/bash -e

GIT_ROOT=$(git rev-parse --show-toplevel)
source $GIT_ROOT/docker_common/utils.sh

REPO_NAME=umd_data605
IMAGE_NAME=umd_data605_template

remove_container_image
