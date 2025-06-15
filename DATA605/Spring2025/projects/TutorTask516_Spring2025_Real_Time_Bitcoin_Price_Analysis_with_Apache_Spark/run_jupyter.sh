#!/bin/bash
source /etc/profile

jupyter lab \
  --port=8888 \
  --ip=0.0.0.0 \
  --no-browser \
  --allow-root \
  --NotebookApp.token='' \
  --NotebookApp.password=''
