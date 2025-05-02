#!/bin/bash

# Stop and remove containers
docker-compose down

# Remove data directories
rm -rf data/zookeeper data/kafka

# Create data directories
mkdir -p data/zookeeper/data data/zookeeper/log data/kafka

# Start containers
docker-compose up -d