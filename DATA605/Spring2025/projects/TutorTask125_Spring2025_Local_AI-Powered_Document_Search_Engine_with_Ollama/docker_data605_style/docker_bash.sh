#!/bin/bash -xe

REPO_NAME=umd_data605

IMAGE_NAME=ollama-notebook
CONTAINER_NAME=ollama-notebook

docker image ls $IMAGE_NAME

# Run container with Jupyter, Streamlit and Ollama ports
docker run \
    -p 8888:8888 \
    -p 8501:8501 \
    -p 11434:11434 \
    -v $(pwd):/app \
    -v /home:/data/home \
    -v /Documents:/data/documents \
    --name $CONTAINER_NAME \
    $IMAGE_NAME