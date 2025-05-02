# Use official Python base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    sudo \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy project files into container
COPY . /app

# Install Python packages
RUN pip install --upgrade pip && \
    pip install \
        faust-streaming \
        requests \
        pandas \
        matplotlib \
        statsmodels \
        jupyterlab

# Expose ports for Jupyter and Faust
EXPOSE 8888 6066

# Run Jupyter by default (can override in exec scripts)
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]
