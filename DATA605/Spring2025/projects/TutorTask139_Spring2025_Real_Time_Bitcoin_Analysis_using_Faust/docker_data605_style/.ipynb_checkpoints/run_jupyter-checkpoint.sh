#!/bin/bash

echo "🚀 Starting JupyterLab..."

jupyter lab \
  --ip=0.0.0.0 \
  --port=8888 \
  --NotebookApp.token='' \
  --NotebookApp.password='' \
  --allow-root
