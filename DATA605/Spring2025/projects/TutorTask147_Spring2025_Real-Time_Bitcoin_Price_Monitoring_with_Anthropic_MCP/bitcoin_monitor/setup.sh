#!/bin/bash

# Create data directory for persistent storage
mkdir -p data

# Check if .env file exists
if [ ! -f .env ]; then
  echo "Creating .env file. Please edit it with your Anthropic API key."
  cp .env.example .env
  echo "Please edit the .env file with your API keys and run this script again."
  exit 1
fi

# Build the Docker image
echo "Building Docker image..."
docker-compose build

echo "Setup complete! Run 'docker-compose up' to start the Bitcoin monitor."