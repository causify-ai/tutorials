#!/bin/bash
docker run -it --rm -p 8888:8888 -v $(pwd):/app bitcoin_env jupyter notebook --ip=0.0.0.0 --allow-root --no-browser
