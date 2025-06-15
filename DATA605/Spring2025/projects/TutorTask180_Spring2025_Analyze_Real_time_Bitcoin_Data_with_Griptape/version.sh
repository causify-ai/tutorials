#!/bin/bash

echo "=== Python Version ==="
python3 --version

echo -e "\n=== Pip Version ==="
pip3 --version

echo -e "\n=== Jupyter Version ==="
jupyter --version

echo -e "\n=== PyArrow Version ==="
python3 -c "import pyarrow as pa; print('PyArrow:', pa.__version__)"

echo -e "\n=== Pandas Version ==="
python3 -c "import pandas as pd; print('Pandas:', pd.__version__)"

echo -e "\n=== Requests Version ==="
python3 -c "import requests; print('Requests:', requests.__version__)"

echo -e "\n=== Matplotlib Version ==="
python3 -c "import matplotlib; print('Matplotlib:', matplotlib.__version__)"

echo -e "\n=== Seaborn Version ==="
python3 -c "import seaborn as sns; print('Seaborn:', sns.__version__)"

echo -e "\n=== Scikit-learn Version ==="
python3 -c "import sklearn; print('Scikit-learn:', sklearn.__version__)"

echo -e "\n=== Griptape Version ==="
python3 -c "import griptape; print('Griptape:', griptape.__version__)"
