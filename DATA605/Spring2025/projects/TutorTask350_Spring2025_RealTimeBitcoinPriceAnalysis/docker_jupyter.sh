#!/bin/bash
docker rm -f bitcoin_analysis 2>/dev/null
docker run -it --rm -p 8888:8888 -p 3333:3333 \
  -v "$(pwd)":/home/jovyan/work \
  --name bitcoin_analysis \
  bitcoin_analysis \
  bash -c "start-notebook.py --NotebookApp.token='' & /opt/openrefine/refine -p 3333 -i 0.0.0.0"
