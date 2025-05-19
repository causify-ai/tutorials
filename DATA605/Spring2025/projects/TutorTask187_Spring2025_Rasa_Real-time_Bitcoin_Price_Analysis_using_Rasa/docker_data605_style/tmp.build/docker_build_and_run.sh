#!/usr/bin/env bash
set -e

IMAGE="btc-chatbot"
CONTAINER="btc-chatbot"

# remove any old container
if docker ps -a --format '{{.Names}}' | grep -xq "$CONTAINER"; then
  docker stop  $CONTAINER
  docker rm    $CONTAINER
fi

echo "🔨 Building image $IMAGE…"
# use parent dir as build context so COPY ../ works
docker build -t $IMAGE ..

echo "🚀 Running container $CONTAINER on port 8501…"
docker run -d --name $CONTAINER -p 8501:8501 $IMAGE

echo "✅ Done! Your app should be live at http://localhost:8501"
