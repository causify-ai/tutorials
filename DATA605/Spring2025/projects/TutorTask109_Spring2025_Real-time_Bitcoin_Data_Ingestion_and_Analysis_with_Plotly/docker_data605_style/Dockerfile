# Use a slim Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /workspace

# Install OS packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    sudo \
    && apt-get clean

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . /workspace

# Expose Jupyter Notebook port
EXPOSE 8888

# Run Jupyter
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--NotebookApp.token=''"]