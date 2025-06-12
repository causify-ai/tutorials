#!/bin/bash
# Stop and remove all containers/images for cleanup
docker stop $(docker ps -aq) 2>/dev/null
docker rm $(docker ps -aq) 2>/dev/null
docker rmi bitcoin-viz -f 2>/dev/null