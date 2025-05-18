#!/bin/bash

# Step 1: Build Docker image
docker build -t bitcoin-nlp .

# Step 2: Run container and mount current folder
docker run -p 8888:8888 -v $(pwd):/app bitcoin-nlp
