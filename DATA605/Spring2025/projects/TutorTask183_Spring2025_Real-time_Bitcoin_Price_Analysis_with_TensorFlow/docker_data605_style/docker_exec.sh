#!/bin/bash -e

GIT_ROOT=$(git rev-parse --show-toplevel)
source $GIT_ROOT/tutorial_github_simple/docker_common/utils.sh

REPO_NAME=umd_data605
IMAGE_NAME=umd_data605_real_time_bitcoin_price_analysis_with_tensorflow

exec_container
