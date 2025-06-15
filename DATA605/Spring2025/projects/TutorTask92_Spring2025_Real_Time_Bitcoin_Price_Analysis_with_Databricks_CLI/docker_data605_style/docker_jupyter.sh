set -xeuo pipefail

REPO_NAME=umd_data605
IMAGE_NAME=bitcoin_cli_project
FULL_IMAGE_NAME="${REPO_NAME}/${IMAGE_NAME}"
CONTAINER_NAME="${IMAGE_NAME}_jupyter"
JUPYTER_HOST_PORT=8888
MOUNT_CFG=""

# 1) Figure out where the host’s .databrickscfg really lives
if [[ "$(uname -o 2>/dev/null)" =~ Msys|Cygwin ]]; then
  if command -v cygpath &>/dev/null; then
    TEST_CFG="$(cygpath -u ~/.databrickscfg)"
    WIN_PATH="$(cygpath -w ~/.databrickscfg | sed 's|\\|/|g')"
  else
    TEST_CFG="${HOME}/.databrickscfg"
    WIN_PATH="$(cmd.exe /C "echo %USERPROFILE%" 2>/dev/null | tr -d '\r')/.databrickscfg"
  fi
else
  TEST_CFG="${HOME}/.databrickscfg"
  WIN_PATH="$TEST_CFG"
fi

# 2) If the config exists on the host, prepare the mount
if [[ -f "$TEST_CFG" ]]; then
  echo "→ mounting Databricks config from $WIN_PATH"
  MOUNT_CFG="-v ${WIN_PATH}:/root/.databrickscfg:ro"
else
  echo "no config found at $TEST_CFG; CLI calls will fail"
fi

# 3) Determine your project folder (Windows vs. Linux pathing)
if [[ "$(uname -o 2>/dev/null)" =~ Msys|Cygwin ]]; then
  HOST_DIR="$(pwd -W)"
else
  HOST_DIR="$(pwd)"
fi

docker image ls "${FULL_IMAGE_NAME}"

# 4) Run container: mount config, mount code, then inside do a mount check & launch Jupyter
docker run --rm -it \
  --name "${CONTAINER_NAME}" \
  -p "${JUPYTER_HOST_PORT}:${JUPYTER_HOST_PORT}" \
  ${MOUNT_CFG} \
  -v "${HOST_DIR}:/data" \
  "${FULL_IMAGE_NAME}" \
  bash -lc '\
    if [ -f /root/.databrickscfg ]; then \
      echo "/root/.databrickscfg is mounted"; \
    else \
      echo "/root/.databrickscfg NOT found"; \
    fi; \
    cd /data && \
    jupyter notebook --no-browser --ip=0.0.0.0 --port='"${JUPYTER_HOST_PORT}"' --allow-root \
  '