#!/bin/bash

# -----------------------------------------------------------------------------
# This script launches a standalone Jupyter Notebook environment
# outside the Airflow container stack.
#
# Usage:
#   bash docker_jupyter.sh
#
# It mounts the current project directory for access to notebooks and data.
# This is helpful for exploring or debugging `*.ipynb` files like:
#   - bitcoin.API.ipynb
#   - bitcoin.example.ipynb
#
# NOTE: This is separate from the Airflow environment. DAGs, logs, or
# Airflow-specific paths (like /opt/airflow/data) are not accessible inside
# this notebook container unless you manually map them.
# -----------------------------------------------------------------------------

docker run -it --rm -p 8888:8888 -v $(pwd):/home/jovyan/work jupyter/base-notebook
