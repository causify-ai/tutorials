source ./docker_name.sh

echo "Building Docker image: $IMAGE_NAME"
docker build -t $IMAGE_NAME .
