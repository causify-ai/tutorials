#!/usr/bin/env bash
set -e

# Build then launch Jupyter
./docker_build.sh

VERSION=$(bash version.sh)
IMAGE=$(bash docker_name.sh)

docker run --rm -it \
  -v "$(pwd)":/home/jovyan/project \
  -p 8888:8888 \
  "${IMAGE}:${VERSION}"