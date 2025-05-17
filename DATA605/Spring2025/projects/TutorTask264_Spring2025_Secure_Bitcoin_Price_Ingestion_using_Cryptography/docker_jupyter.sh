#!/usr/bin/env bash
set -e

docker run --rm -it \
  -v "$(pwd)":/app \
  -p 8888:8888 \
  securebitcoin_data605 \
  jupyter notebook \
    --ip=0.0.0.0 \
    --port=8888 \
    --no-browser \
    --allow-root \
    --NotebookApp.token='' \
    --NotebookApp.password='' \
    --ServerApp.token='' \
    --ServerApp.password=''
