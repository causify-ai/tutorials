#!/bin/bash -e

# Set project-specific names
REPO_NAME=tutortask123
IMAGE_NAME=btc_trade_huey_pipeline

# Exec into a running container (if running)
docker exec -it $IMAGE_NAME /bin/bash
