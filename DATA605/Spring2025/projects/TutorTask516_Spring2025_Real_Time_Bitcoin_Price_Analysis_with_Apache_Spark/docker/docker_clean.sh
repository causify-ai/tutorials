#!/bin/bash
docker rm -f $(docker ps -aq)
docker rmi -f bitcoin_project
docker system prune -f
