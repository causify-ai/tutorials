#!/bin/bash
docker run -it --rm -p 8888:8888 -p 8001:8001 -v $(pwd):/app bitcoin_env bash
