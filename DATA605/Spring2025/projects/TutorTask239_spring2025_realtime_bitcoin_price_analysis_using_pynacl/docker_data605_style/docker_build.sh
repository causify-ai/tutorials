#!/bin/bash

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Build the Docker image
docker build -t bitcoin-analysis:latest \
    --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
    --build-arg VCS_REF=$(git rev-parse --short HEAD) \
    -f "$SCRIPT_DIR/Dockerfile" \
    "$SCRIPT_DIR/.."

# Save build info
docker inspect bitcoin-analysis:latest > "$SCRIPT_DIR/docker_build.version.log"
