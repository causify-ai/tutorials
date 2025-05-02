#!/bin/bash

echo "🧹 Cleaning up Docker containers and images..."

# Stop all running containers
docker ps -q | xargs -r docker stop

# Remove all containers
docker ps -a -q | xargs -r docker rm

# Remove all dangling images
docker images -f "dangling=true" -q | xargs -r docker rmi

# Remove all unused volumes (optional)
docker volume prune -f

echo "✅ Docker cleanup complete."
