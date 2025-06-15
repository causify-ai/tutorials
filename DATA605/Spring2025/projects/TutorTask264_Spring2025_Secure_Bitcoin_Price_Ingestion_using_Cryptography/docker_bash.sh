#!/usr/bin/env bash
docker run --rm -it \
  -v "$(pwd)":/app \
  -p 8888:8888 \
  securebitcoin_data605 \
  bash
