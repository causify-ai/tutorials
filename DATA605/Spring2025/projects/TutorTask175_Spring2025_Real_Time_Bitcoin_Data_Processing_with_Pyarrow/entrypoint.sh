#!/bin/bash

echo "📦 Running main.py to fetch and process data..."
python data_ingestion/main.py

echo "🚀 Starting Jupyter Notebook..."
jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root --no-browser
