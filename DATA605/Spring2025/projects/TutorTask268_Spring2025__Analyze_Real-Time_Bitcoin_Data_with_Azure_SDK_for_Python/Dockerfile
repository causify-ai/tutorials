# Use official Python image with common tools
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system packages and pip
RUN apt-get update && apt-get install -y git curl && \
    pip install --upgrade pip

# Copy your requirements and install
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of your project
COPY . .

# Expose Jupyter port
EXPOSE 8888

# Default command to run bash (override in shell scripts)
CMD ["/bin/bash"]
