#!/bin/bash
# Start a Jupyter notebook server inside the container, mounting the current directory

docker run --rm -it \
    -v "$(pwd)":/app \
    -p 8888:8888 \
    bigdl-bitcoin:latest \
    jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root --no-browser --NotebookApp.token=''
