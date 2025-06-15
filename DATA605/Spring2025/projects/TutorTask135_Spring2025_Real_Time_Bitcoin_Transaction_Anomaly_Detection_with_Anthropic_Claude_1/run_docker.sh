#!/bin/bash

docker run -i --rm \
  -p 8888:8888 \
  -v "$(pwd)":/workspace \
  umd_data605/umd_data605_template \
  bash run_jupyter.sh &

# Wait 5 seconds and open in browser
sleep 5
open http://localhost:8888