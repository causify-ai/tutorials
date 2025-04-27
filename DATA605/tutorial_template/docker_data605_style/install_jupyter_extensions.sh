#!/bin/bash

# Install Jupyter Notebook extensions
pip install jupyter_contrib_nbextensions

# Enable extensions
jupyter contrib nbextension install --user
../../../../../docker_common/install_jupyter_extensions.sh
