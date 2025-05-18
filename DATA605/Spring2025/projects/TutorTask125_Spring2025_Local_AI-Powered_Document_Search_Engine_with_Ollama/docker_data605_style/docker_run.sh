#!/bin/bash -xe

IMAGE_NAME=ollama-notebook
CONTAINER_NAME=ollama-notebook

# Check if container already exists and remove it
if [ "$(docker ps -a -q -f name=$CONTAINER_NAME)" ]; then
    docker stop $CONTAINER_NAME || true
    docker rm $CONTAINER_NAME || true
fi

# Run container in detached mode with additional port and mounts
docker run -d \
    --name $CONTAINER_NAME \
    -p 8888:8888 \
    -p 8501:8501 \
    -p 11434:11434 \
    -v $(pwd):/app \
    -v /home:/data/home \
    -v /Documents:/data/documents \
    $IMAGE_NAME

echo "Container started!"
echo "Access the Streamlit app at: http://localhost:8501"
echo "Access Jupyter Notebook at: http://localhost:8888"
echo "To view logs, run: docker logs -f $CONTAINER_NAME" 