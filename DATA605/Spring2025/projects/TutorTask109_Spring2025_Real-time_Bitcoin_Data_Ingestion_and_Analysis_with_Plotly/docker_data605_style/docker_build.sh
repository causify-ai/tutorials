#!/bin/bash
# Build the Docker image and log output
docker build -t bitcoin-viz . | tee docker_build.log