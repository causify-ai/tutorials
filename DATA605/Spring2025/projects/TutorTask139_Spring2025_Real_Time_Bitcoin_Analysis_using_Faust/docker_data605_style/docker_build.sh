#!/bin/bash

# Name of the image
IMAGE_NAME="faust-bitcoin-analysis"

echo "🚀 Building Docker image: $IMAGE_NAME"
docker build -t $IMAGE_NAME .

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
else
    echo "❌ Build failed."
    exit 1
fi
