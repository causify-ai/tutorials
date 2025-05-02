#!/bin/bash

# Set your DockerHub username and image name
USERNAME="your_dockerhub_username"
IMAGE_NAME="faust-bitcoin-analysis"
TAG="latest"

FULL_NAME="$USERNAME/$IMAGE_NAME:$TAG"

echo "📦 Tagging image as: $FULL_NAME"
docker tag $IMAGE_NAME $FULL_NAME

echo "🚀 Pushing image to Docker Hub..."
docker push $FULL_NAME

if [ $? -eq 0 ]; then
    echo "✅ Push successful!"
else
    echo "❌ Push failed. Check credentials or image name."
fi
