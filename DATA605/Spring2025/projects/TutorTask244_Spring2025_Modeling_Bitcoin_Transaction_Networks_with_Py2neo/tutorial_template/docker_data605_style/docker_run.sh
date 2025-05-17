#!/bin/bash

# Constants
IMAGE_NAME="umd_data605_template"
NETWORK_NAME="neo4j-net"
NEO4J_NAME="my_neo4j"
NEO4J_PASSWORD="test12345"

# Step 1: Create Docker network if needed
./docker_network.sh

# Step 2: Start Neo4j container (if not running)
if ! docker ps --format '{{.Names}}' | grep -q "^$NEO4J_NAME$"; then
  echo "Starting Neo4j container..."
  docker run -d \
    --name $NEO4J_NAME \
    --network $NETWORK_NAME \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/$NEO4J_PASSWORD \
    neo4j
else
  echo "Neo4j container already running."
fi

# Step 3: Run your Jupyter container
echo "Starting Jupyter container..."
docker run -it --rm \
  --network $NETWORK_NAME \
  -p 8888:8888 \
  -v $(pwd)/..:/workspace \
  -w /workspace \
  -e NEO4J_URI=bolt://my_neo4j:7687 \
  -e NEO4J_USER=neo4j \
  -e NEO4J_PASS=test12345 \
  $IMAGE_NAME \
  jupyter notebook --ip=0.0.0.0 --no-browser --allow-root --notebook-dir=/workspace

