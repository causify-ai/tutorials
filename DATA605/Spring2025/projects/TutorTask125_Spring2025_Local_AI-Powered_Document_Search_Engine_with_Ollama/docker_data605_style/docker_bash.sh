#!/bin/bash -xe

REPO_NAME=umd_data605
IMAGE_NAME=document_search_engine
FULL_IMAGE_NAME=$IMAGE_NAME

docker image ls $FULL_IMAGE_NAME

	@@ -11,5 +11,5 @@ docker run -d \
    --name $CONTAINER_NAME \
    -p 8501:8501 \
    -p 11434:11434 \
    -v $(pwd):/app \
    $FULL_IMAGE_NAME