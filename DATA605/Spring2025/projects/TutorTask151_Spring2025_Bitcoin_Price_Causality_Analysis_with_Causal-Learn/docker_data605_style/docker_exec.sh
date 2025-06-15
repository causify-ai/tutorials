#!/usr/bin/env bash
set -e

# Run a shell inside the built image, mounting your project for live edits
VERSION=$(bash version.sh)
IMAGE=$(bash docker_name.sh)

docker run --rm -it \
  -v "$(pwd)":/home/jovyan/project \
  -p 8888:8888 \
  "${IMAGE}:${VERSION}" bash