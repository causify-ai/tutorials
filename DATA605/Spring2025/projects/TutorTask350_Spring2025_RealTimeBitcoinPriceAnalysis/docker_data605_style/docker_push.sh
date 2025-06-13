#!/bin/bash -e

GIT_ROOT=$(git rev-parse --show-toplevel)
source $GIT_ROOT/tutorial_github_simple/docker_common/utils.sh

REPO_NAME=umd_data605
IMAGE_NAME=umd_data605_template

push_container_image
