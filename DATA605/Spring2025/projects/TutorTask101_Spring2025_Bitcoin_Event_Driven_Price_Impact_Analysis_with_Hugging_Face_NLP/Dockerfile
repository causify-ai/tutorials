FROM python:3.10-slim

# Set up environment
WORKDIR /app
COPY . /app

# Install Python dependencies including PyTorch
RUN pip install --no-cache-dir torch torchvision torchaudio \
    transformers pandas numpy matplotlib jupyter

# Expose port for Jupyter
EXPOSE 8888

# Default command to run Jupyter
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
