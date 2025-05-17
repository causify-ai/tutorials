#!/bin/bash -xe

jupyter-notebook \
    --port=${JUPYTER_HOST_PORT:-8888} \
    --no-browser --ip=0.0.0.0 \
    --allow-root \
    --NotebookApp.token='' --NotebookApp.password=''
