#!/bin/bash -xe
cd ~/src/venv
python3 -m venv mkdocs
source mkdocs/bin/activate
pip install mkdocs-material

echo "Activate with: source $HOME/src/venv/mkdocs/bin/activate"
