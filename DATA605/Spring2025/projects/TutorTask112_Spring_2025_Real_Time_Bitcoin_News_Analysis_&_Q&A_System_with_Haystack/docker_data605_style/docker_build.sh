#!/bin/bash
FULL_IMAGE_NAME=bitcoin_haystack:latest
echo "🔨 Building Docker image: $FULL_IMAGE_NAME"
docker build -t $FULL_IMAGE_NAME .
echo "✅ Build complete."
