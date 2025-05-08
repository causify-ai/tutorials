#!/bin/bash
echo " Stopping and removing containers..."
docker stop bitcoin-haystack es-bitcoin
docker rm bitcoin-haystack es-bitcoin
docker system prune -f
