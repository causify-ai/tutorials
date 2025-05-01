#!/bin/bash
# Run the Docker container and mount the parent folder (safe for spaces)

PARENT_DIR="$(cd .. && pwd)"

docker run -it \
  --name bitcoin_container \
  -p 8888:8888 \
  -v "${PARENT_DIR}:/workspace" \
  bitcoin-viz