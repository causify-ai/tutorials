#!/bin/bash
docker run -it --rm \
    -p 8888:8888 \
    -v "$(pwd)/../..:/data" \
    --name bitcoin_analysis \
    data605 \
    jupyter lab --ip=0.0.0.0 --allow-root
