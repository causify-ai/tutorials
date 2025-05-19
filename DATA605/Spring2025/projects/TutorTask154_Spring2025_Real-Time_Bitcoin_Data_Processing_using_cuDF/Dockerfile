FROM rapidsai/rapidsai-core:24.04-cuda12.0-runtime-ubuntu22.04-py3.10

# Set working directory
WORKDIR /app

# Copy project files
COPY notebook/ /app/notebook/
COPY utils/ /app/utils/
COPY README.md /app/
COPY requirements.txt /app/
COPY run_jupyter.sh /app/
COPY install_jupyter_extensions.sh /app/

# Install additional Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Make scripts executable
RUN chmod +x /app/run_jupyter.sh /app/install_jupyter_extensions.sh

# Install Jupyter extensions
RUN /app/install_jupyter_extensions.sh

# Expose Jupyter port
EXPOSE 8888

# Start Jupyter Notebook
CMD ["/app/run_jupyter.sh"]
