#!/bin/bash

echo "Starting Jupyter Lab at http://localhost:8888 ..."
jupyter lab --ip=0.0.0.0 --port=8888 --allow-root --no-browser --NotebookApp.token='' --NotebookApp.password='' &

echo "Starting Streamlit Dashboard at http://localhost:8501 ..."
streamlit run btc_dashboard.py --server.port=8501 --server.address=0.0.0.0 &

# Keep the container alive
tail -f /dev/null
