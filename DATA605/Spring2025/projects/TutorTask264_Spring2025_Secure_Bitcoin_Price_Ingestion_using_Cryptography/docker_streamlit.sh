#!/usr/bin/env bash
set -e

docker run --rm -it \
  -v "$(pwd)":/app \
  -p 8501:8501 \
  securebitcoin_data605 \
  streamlit run streamlit_app.py \
    --server.port=8501 \
    --server.address=0.0.0.0
