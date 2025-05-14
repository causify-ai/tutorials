#!/bin/bash

# Generate Jupyter config if not present
jupyter notebook --generate-config -y

# Disable authentication
echo "c.ServerApp.token = ''" >> /root/.jupyter/jupyter_server_config.py
echo "c.ServerApp.password = ''" >> /root/.jupyter/jupyter_server_config.py
echo "c.ServerApp.allow_origin = '*'" >> /root/.jupyter/jupyter_server_config.py
echo "c.ServerApp.allow_remote_access = True" >> /root/.jupyter/jupyter_server_config.py
echo "c.ServerApp.ip = '0.0.0.0'" >> /root/.jupyter/jupyter_server_config.py
echo "c.ServerApp.open_browser = False" >> /root/.jupyter/jupyter_server_config.py
echo "c.ServerApp.port = 8888" >> /root/.jupyter/jupyter_server_config.py

# Start Jupyter and Streamlit
echo "Starting JupyterLab on port 8888..."
jupyter lab &

echo "Starting Streamlit on port 8502..."
streamlit run btc_dashboard.py --server.port=8502 --server.address=0.0.0.0
