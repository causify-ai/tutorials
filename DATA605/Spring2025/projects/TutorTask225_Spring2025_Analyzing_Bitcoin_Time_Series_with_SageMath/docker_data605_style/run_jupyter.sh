#!/bin/bash

docker run -it --rm \
  -p 8899:8888 \
  -v /Users/adariprasad/src/tutorials1/DATA605/Spring2025/projects/TutorTask225_Spring2025_Analyzing_Bitcoin_Time_Series_with_SageMath/bitcoin-timeseries:/home/sage/project \
  sage-btc \
  sage -n jupyterlab --ip=0.0.0.0 --port=8888 --no-browser --notebook-dir=/home/sage/project
