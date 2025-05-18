FROM python:3.10-slim

WORKDIR /app

# Install system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Jupyter + dependencies
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install jupyter jupyterlab

# Set environment variables
ENV PYTHONPATH=/app:$PYTHONPATH
ENV JUPYTER_ENABLE_LAB=yes
ENV JUPYTER_CONFIG_DIR=/app/.jupyter
ENV JUPYTER_DATA_DIR=/app/.jupyter/data
ENV JUPYTER_RUNTIME_DIR=/app/.jupyter/runtime

# Create Jupyter config directory and set permissions
RUN mkdir -p /app/.jupyter/data /app/.jupyter/runtime && \
    chmod -R 777 /app/.jupyter

# Copy project files
COPY . .

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

