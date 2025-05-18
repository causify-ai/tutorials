#!/usr/bin/env bash
set -e

# Load version and image name
VERSION=$(bash version.sh)            # ← make sure this actually echoes something—
IMAGE=$(bash docker_name.sh)

# Build with both a version tag and “latest”
docker build \
  -t "${IMAGE}:${VERSION}" \
  -t "${IMAGE}:latest" \
  .
