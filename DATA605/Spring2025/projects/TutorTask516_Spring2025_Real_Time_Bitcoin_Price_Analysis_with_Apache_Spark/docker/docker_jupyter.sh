#!/bin/bash
docker run -it --rm \
    -p 8888:8888 \
    -v "$PWD":/workspace \
    bitcoin_project
