#!/bin/bash
set -e

# Start Falcon API in the background
uvicorn Falcon_ingest_endpoint2:app --host 0.0.0.0 --port 8888 --reload &

# Start Jupyter Notebook on port 8889
exec jupyter-notebook \
  --port=8889 \
  --no-browser \
  --ip=0.0.0.0 \
  --allow-root \
  --NotebookApp.token='' \
  --NotebookApp.password=''
