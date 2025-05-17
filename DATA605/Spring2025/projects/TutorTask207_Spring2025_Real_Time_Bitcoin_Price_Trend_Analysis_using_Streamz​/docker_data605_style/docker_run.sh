#!/usr/bin/env bash

# 1. Build the image
./docker_build.sh

# 2. Remove old container (if any)
docker rm -f data605_streamz >/dev/null 2>&1 || true

# 3. Start the container (detached, mounts your code, maps 8888)
docker run -d \
  --name data605_streamz \
  -p 8888:8888 \
  -v "$(pwd):/home/jovyan/work" \
  data605_bitcoin:$(./version.sh) \
  tail -f /dev/null

# 4. Launch Jupyter inside the new container
docker exec -d data605_streamz /home/jovyan/work/run_jupyter.sh

echo "✅ Container is up!  Jupyter → http://localhost:8888"
