#!/bin/bash
echo "🚀 Running main.py to update data..."
python pipeline/main.py

echo "✅ Data update complete. Launching Jupyter Notebook..."
jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --NotebookApp.password=''
