#!/bin/bash -e

REPO_NAME=umd_data605
IMAGE_NAME=data605-btc-project

# Set the volume mount to your full project path
PROJECT_DIR="$HOME/src/tutorials/DATA605/Spring2025/projects/TutorTask65_Spring2025_Real_Time_Bitcoin_Price_Processing_with_Amazon_Lambda"

docker run --rm -ti \
  --name $IMAGE_NAME \
  -p 8888:8888 \
  -v "$PROJECT_DIR:/app" \
  -w /app \
  $IMAGE_NAME \
  jupyter-notebook --port=8888 --no-browser --ip=0.0.0.0 --allow-root
