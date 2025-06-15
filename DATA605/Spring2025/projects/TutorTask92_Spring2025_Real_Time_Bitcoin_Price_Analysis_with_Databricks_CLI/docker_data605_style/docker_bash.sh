#!/bin/bash -xe

set -xeuo pipefail

REPO_NAME=umd_data605
IMAGE_NAME=bitcoin_cli_project
FULL_IMAGE_NAME="${REPO_NAME}/${IMAGE_NAME}"
CONTAINER_NAME="${IMAGE_NAME}_bash"

MOUNT_CFG=""
if [[ "$(uname -o 2>/dev/null)" =~ Msys|Cygwin ]]; then
  if command -v cygpath &>/dev/null; then
    HOST_CFG_PATH="$(cygpath -w ~/.databrickscfg | sed 's|\\|/|g')"
  else
    WIN_HOME="$(cmd.exe /C "echo %USERPROFILE%" 2>/dev/null | tr -d '\r')"
    HOST_CFG_PATH="${WIN_HOME}/.databrickscfg"
  fi
else
  HOST_CFG_PATH="${HOME}/.databrickscfg"
fi

USER_HOME=$(docker run --rm "${FULL_IMAGE_NAME}" bash -lc 'echo $HOME')

MOUNT_CFG="-v ${HOST_CFG_PATH}:/root/.databrickscfg:ro"

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
  -v "${HOST_CFG_PATH}:${USER_HOME}/.databrickscfg:ro" \
  "${FULL_IMAGE_NAME}" \
    -lc ' \
    if [ -f /root/.databrickscfg ]; then \
      echo "/root/.databrickscfg is mounted"; \
    else \
      echo "/root/.databrickscfg NOT found"; \
    fi; \
    exec bash \
    '