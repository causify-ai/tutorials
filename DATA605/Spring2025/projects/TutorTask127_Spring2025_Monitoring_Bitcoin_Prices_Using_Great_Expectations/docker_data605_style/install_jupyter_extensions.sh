#!/bin/bash -e

echo "Installing Jupyter Notebook extensions..."

# Install necessary Jupyter extensions and related packages
pip install --no-cache-dir \
    jupyter-contrib-nbextensions \
    jupyter_nbextensions_configurator \
    jupyter-highlight-selected-word

# Enable extensions at system level
jupyter contrib nbextension install --system
jupyter nbextensions_configurator enable --system

echo "Jupyter extensions installed successfully!"
