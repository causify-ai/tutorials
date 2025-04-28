#!/bin/bash

docker run -it --rm \
  -p 8888:8888 \
  --name data605_project_container \
  data605_project_image \
  bash

