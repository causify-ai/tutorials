#!/bin/bash
set -e

echo "Installing Jupyter extensions..."
pip3 install jupyter_contrib_nbextensions
jupyter contrib nbextension install --user
