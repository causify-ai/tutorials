#!/bin/bash
docker run -it --rm \
    -p 8888:8888 \
    -v "/Users/pravija/Documents/tutorials:/workspace" \
    --name bitcoin_analysis \
    bitcoin \
    jupyter lab --ip=0.0.0.0 --allow-root --notebook-dir=/workspace   
    
