#!/bin/bash

echo " Python Version "
python3 --version

echo " Pip Version "
pip3 --version

echo " Jupyter Version "
jupyter --version

echo " PyArrow Version "
python3 -c "import pyarrow as pa; print('PyArrow', pa.__version__)"

echo " Pandas Version "
python3 -c "import pandas as pd; print('Pandas', pd.__version__)"

echo " Requests Version "
python3 -c "import requests; print('Requests', requests.__version__)"

echo " Matplotlib Version "
python3 -c "import matplotlib; print('Matplotlib', matplotlib.__version__)"
