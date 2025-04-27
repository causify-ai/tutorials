FROM rapidsai/rapidsai-core:cuda11.8-runtime-ubuntu20.04-py3.9

# Set working directory
WORKDIR /app

# Copy project files
COPY notebook/ /app/notebook/
COPY utils/ /app/utils/
COPY README.md /app/
COPY requirements.txt /app/

# Install additional Python packages
RUN pip install --no-cache-dir \
    jupyter \
    pandas \
    plotly \
    requests \
    python-dotenv 

# Expose Jupyter port
EXPOSE 8888

# Start Jupyter Notebook
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--allow-root", "--NotebookApp.token=''"]
