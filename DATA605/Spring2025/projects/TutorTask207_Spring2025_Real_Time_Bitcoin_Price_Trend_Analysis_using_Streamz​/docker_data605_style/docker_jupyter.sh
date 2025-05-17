#!/usr/bin/env bash
# launch Jupyter inside the running container,
# binding to 0.0.0.0 so you can access it on your host
docker exec -d data605_streamz \
  jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root
