FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies in specific order
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir numpy==1.24.3 && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir \
    jupyter \
    notebook \
    ipywidgets \
    jupyterlab

# Copy source code and notebooks
COPY src/ /app/src/
COPY Advanced_BitCoin_Sentiment.ipynb /app/
COPY data/ /app/data/
COPY logs/ /app/logs/

# Create necessary directories
RUN mkdir -p /app/data /app/logs

# Set environment variables
ENV PYTHONPATH=/app:$PYTHONPATH
ENV JUPYTER_ENABLE_LAB=yes
ENV JUPYTER_CONFIG_DIR=/app/.jupyter
ENV JUPYTER_DATA_DIR=/app/.jupyter/data
ENV JUPYTER_RUNTIME_DIR=/app/.jupyter/runtime

# Create Jupyter config directory and set permissions
RUN mkdir -p /app/.jupyter/data /app/.jupyter/runtime && \
    chmod -R 777 /app/.jupyter

# Expose Jupyter port
EXPOSE 8888

# Start Jupyter notebook with specific settings
CMD ["jupyter", "notebook", \
     "--ip=0.0.0.0", \
     "--port=8888", \
     "--no-browser", \
     "--allow-root", \
     "--NotebookApp.token=''", \
     "--NotebookApp.password=''", \
     "--NotebookApp.notebook_dir=/app", \
     "--NotebookApp.allow_origin='*'", \
     "--NotebookApp.allow_remote_access=True"] 