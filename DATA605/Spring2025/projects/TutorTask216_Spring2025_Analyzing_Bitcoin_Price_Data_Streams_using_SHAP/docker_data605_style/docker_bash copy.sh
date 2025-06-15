
#!/bin/bash -xe

REPO_NAME=umd_data605
IMAGE_NAME=bitcoin_price_data_using_shap
FULL_IMAGE_NAME=$REPO_NAME/$IMAGE_NAME

docker image ls $FULL_IMAGE_NAME

CONTAINER_NAME=$IMAGE_NAME
docker run --rm -it \
    --name $CONTAINER_NAME \
    --entrypoint /bin/bash \
    -v $(pwd):/data \
    $FULL_IMAGE_NAME