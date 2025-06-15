#!/bin/bash

# Remove all Jupyter notebook checkpoint directories
find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} +

# Remove all Python bytecode cache directories
find . -type d -name "__pycache__" -exec rm -rf {} +

# Remove any macOS Finder metadata files
find . -type f -name ".DS_Store" -delete

# Remove any log files (e.g., build logs, etc.)
find . -type f -name "*.log" -delete

echo "Cleanup complete!"

