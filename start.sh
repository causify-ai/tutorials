#!/bin/bash

# Build the Docker image
docker build -t bitcoin-project .

# Run the Docker container with volume mount and AWS credentials
docker run -it --rm \
  -p 8888:8888 \
  -v $(pwd):/app \
  -v ~/.aws:/root/.aws \
  bitcoin-project

