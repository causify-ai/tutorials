#!/bin/bash

# Stop and remove the container
docker stop bitcoin-analysis
docker rm bitcoin-analysis

# Remove the volumes (optional, uncomment if you want to remove all data)
# docker volume rm bitcoin-data
# docker volume rm bitcoin-logs

# Remove the image
docker rmi bitcoin-analysis:latest

echo "Cleanup complete"
