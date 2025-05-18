#!/bin/bash

echo " Building Docker image: bitcoin_realtime_sdk..."
docker build -t bitcoin_realtime_sdk .

if [ $? -ne 0 ]; then
  echo " Docker build failed. Exiting."
  exit 1
fi

echo " Docker image built successfully."

echo " Running the Python pipeline..."
python3 docker_sdk.example.py

echo " Pipeline execution complete."
