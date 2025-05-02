#!/bin/bash

# Run both Jupyter and Streamlit in the background
jupyter notebook --ip=0.0.0.0 --port=8888 --allow-root --NotebookApp.token='' --NotebookApp.password='' &

streamlit run btc_forecast_app.py --server.port=8501 --server.address=0.0.0.0