#!/bin/bash
set -e

# Install Jupyter Nbextensions
pip install jupyter_contrib_nbextensions
jupyter contrib nbextension install --system
