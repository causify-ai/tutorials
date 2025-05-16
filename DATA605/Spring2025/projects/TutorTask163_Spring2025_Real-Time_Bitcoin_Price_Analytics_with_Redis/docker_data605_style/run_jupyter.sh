#!/bin/bash
# Script to start Jupyter notebook and Redis server in the Docker container

# Start Redis server
echo "Starting Redis server..."
sudo /usr/local/bin/start_redis.sh

# Configure environment variables for Redis connection
export REDIS_HOST="localhost"
export REDIS_PORT=6379
export REDIS_PASSWORD=""

# Start Jupyter Notebook
echo "Starting Jupyter Notebook..."
cd /home/jupyter/work || exit
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''
