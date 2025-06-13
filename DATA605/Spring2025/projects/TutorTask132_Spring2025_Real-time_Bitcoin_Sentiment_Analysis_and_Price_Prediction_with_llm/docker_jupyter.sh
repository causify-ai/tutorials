#!/bin/bash
# #
# # Execute run_jupyter.sh in the container.
# # 
# # Usage:
# # > docker_jupyter.sh -d /Users/saggese/src/git_gp1/code/book.2018.Martin.Bayesian_Analysis_with_Python.2e -v -u -p 8889
# #

# set -e
# #set -x

# # Parse params.
# export JUPYTER_HOST_PORT=8888
# export JUPYTER_USE_VIM=0
# export TARGET_DIR=""
# export VERBOSE=0

# OLD_CMD_OPTS=$@
# while getopts p:d:uv flag
# do
#     case "${flag}" in
#         p) JUPYTER_HOST_PORT=${OPTARG};;
#         u) JUPYTER_USE_VIM=1;;
#         d) TARGET_DIR=${OPTARG};;
#         # /Users/saggese/src/git_gp1/code/
#         v) VERBOSE=1;;
#     esac
# done

# if [[ $VERBOSE == 1 ]]; then
#     set -x
# fi;

# # Import the utility functions.
# GIT_ROOT=$(git rev-parse --show-toplevel)
# source $GIT_ROOT/docker_common/utils.sh

# # Execute the script setting the vars for this tutorial.
# get_docker_vars_script ${BASH_SOURCE[0]}
# source $DOCKER_NAME
# print_docker_vars

# # Run the script.
# DOCKER_RUN_OPTS="-p $JUPYTER_HOST_PORT:$JUPYTER_HOST_PORT"
# if [[ $TARGET_DIR != "" ]]; then
#     DOCKER_RUN_OPTS="$DOCKER_RUN_OPTS -v $TARGET_DIR:/data"
# fi;
# CMD="/curr_dir/run_jupyter.sh $OLD_CMD_OPTS"

# # From docker_cmd.sh passing DOCKER_OPTS.
# run "docker image ls $FULL_IMAGE_NAME"
# (docker manifest inspect $FULL_IMAGE_NAME | grep arch) || true

# CONTAINER_NAME=$IMAGE_NAME
# run "docker run \
#     --rm -ti \
#     --name $CONTAINER_NAME \
#     $DOCKER_RUN_OPTS \
#     -v $(pwd):/curr_dir \
#     $FULL_IMAGE_NAME \
#     $CMD"


set -xeuo pipefail

REPO_NAME=umd_data605
IMAGE_NAME=bitcoin_cli_project
FULL_IMAGE_NAME="${REPO_NAME}/${IMAGE_NAME}"
CONTAINER_NAME="${IMAGE_NAME}_jupyter"

# Default Jupyter port
JUPYTER_HOST_PORT=8888
MOUNT_CFG=""

# Parse optional flags
while [[ $# -gt 0 ]]; do
  case "$1" in
    --mount-config)
      # mount host ~/.databrickscfg into container for CLI auth
      MOUNT_CFG="-v ${HOME}/.databrickscfg:/root/.databrickscfg:ro"
      shift
      ;;
    -p|--port)
      JUPYTER_HOST_PORT="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

# Determine host project directory path for Docker
if [[ "$(uname -o 2>/dev/null)" =~ Msys|Cygwin ]]; then
  HOST_DIR="$(pwd -W)"
else
  HOST_DIR="$(pwd)"
fi

# Show the image
docker image ls "${FULL_IMAGE_NAME}"

# Run container and start JupyterLab
docker run --rm -it \
  --name "${CONTAINER_NAME}" \
  -p "${JUPYTER_HOST_PORT}:${JUPYTER_HOST_PORT}" \
  ${MOUNT_CFG} \
  -v "${HOST_DIR}:/data" \
  "${FULL_IMAGE_NAME}" \
  bash -lc "cd /data && jupyter lab --no-browser --ip=0.0.0.0 --port=${JUPYTER_HOST_PORT} --allow-root"