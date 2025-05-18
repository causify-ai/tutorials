#!/bin/bash

# ✅ Lowercase, simple image name
PROJECT_NAME=tutor_task114_s3fs_project

echo "🐳 Building Docker image: $PROJECT_NAME"
docker build -f docker_data605_style/Dockerfile -t $PROJECT_NAME .
