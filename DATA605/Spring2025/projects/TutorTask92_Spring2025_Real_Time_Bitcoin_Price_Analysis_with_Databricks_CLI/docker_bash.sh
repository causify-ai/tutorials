#!/bin/bash -xe

# REPO_NAME=umd_data605
# IMAGE_NAME=bitcoin_cli_project
# FULL_IMAGE_NAME=$REPO_NAME/$IMAGE_NAME

# docker image ls $FULL_IMAGE_NAME

# CONTAINER_NAME=$IMAGE_NAME
# docker run --rm -ti \
#     --name $CONTAINER_NAME \
#     --entrypoint /data \    
#     -p 8888:8888 \
#     -v $(pwd):/data \
#     $FULL_IMAGE_NAME


set -xeuo pipefail

REPO_NAME=umd_data605
IMAGE_NAME=bitcoin_cli_project
FULL_IMAGE_NAME="${REPO_NAME}/${IMAGE_NAME}"
CONTAINER_NAME="${IMAGE_NAME}_bash"

# parse flag
MOUNT_CFG=""
if [[ "${1:-}" == "--mount-config" ]]; then
  MOUNT_CFG="-v ${HOME}/.databrickscfg:/root/.databrickscfg:ro"
fi

# show the image
docker image ls "${FULL_IMAGE_NAME}"

# detect host path
if [[ "$(uname -o 2>/dev/null)" =~ Msys|Cygwin ]]; then
  HOST_DIR="$(pwd -W)"
else
  HOST_DIR="$(pwd)"
fi

# run container, conditionally mounting config
docker run --rm -it \
  --name "${CONTAINER_NAME}" \
  --entrypoint bash \
  -p 8888:8888 \
  ${MOUNT_CFG} \
  -v "${HOST_DIR}:/data" \
  "${FULL_IMAGE_NAME}"