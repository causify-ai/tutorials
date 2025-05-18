#!/bin/bash
# Create a shared Docker network

NETWORK_NAME="neo4j-net"

if ! docker network ls | grep -q $NETWORK_NAME; then
    echo "Creating Docker network: $NETWORK_NAME"
    docker network create $NETWORK_NAME
else
    echo "Docker network $NETWORK_NAME already exists"
fi
