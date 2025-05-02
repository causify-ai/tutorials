#!/bin/bash

echo "🔧 Installing JupyterLab extensions..."

# Install Node.js (required for some Jupyter extensions)
apt-get update && apt-get install -y nodejs npm

# Upgrade pip and JupyterLab
pip install --upgrade pip jupyterlab

# Optional extensions
# pip install jupyterlab_code_formatter
# jupyter labextension install @ryantam626/jupyterlab_code_formatter

# Enable server-side formatting (e.g., with black)
# pip install black isort

echo "✅ Jupyter extensions installed. Restart Jupyter if needed."
