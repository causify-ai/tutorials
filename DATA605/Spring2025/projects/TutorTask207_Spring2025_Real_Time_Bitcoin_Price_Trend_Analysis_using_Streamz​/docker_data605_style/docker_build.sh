#!/usr/bin/env bash
# build with the version tag from version.sh
IMAGE=data605_bitcoin:$(./version.sh)
docker build -t "$IMAGE" .
