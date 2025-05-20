#!/bin/bash

# This script runs Jupyter Notebook inside the Docker container
# and mounts the parent project directory for persistent access.

# Function to handle errors
handle_error() {
    echo "Error: $1"
    exit 1
}

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    handle_error "docker-compose is not installed. Please install it first."
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    handle_error "Docker is not running. Please start Docker first."
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p ../data
chmod 777 ../data

echo "Starting Jupyter Notebook environment..."
echo "This will build and start the Docker containers."
echo "Press Ctrl+C to stop the containers when you're done."

# Build and start the containers
docker-compose up --build || handle_error "Failed to start containers"

# Note: The script will keep running until the user presses Ctrl+C
# This is intentional as we want to keep the containers running 