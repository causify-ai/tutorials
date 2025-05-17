#!/usr/bin/env bash
# remove containers/images used for this project
docker rm -f data605_streamz || true
docker rmi data605_bitcoin:$(./version.sh) || true
