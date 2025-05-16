# Use Python 3.10 as the base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY web_app/frontend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the src and utilities directories
COPY src /app/src
COPY utilities /app/utilities

# Create configs directory and copy config file
RUN mkdir -p /app/configs
COPY configs/config.yaml /app/configs/

# Create data directories (will be mounted as volumes)
RUN mkdir -p /app/data/predictions /app/data/raw_data

# Copy the frontend app
COPY web_app/frontend /app/web_app/frontend

# Expose the port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=web_app/frontend/app.py
ENV FLASK_ENV=development
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "web_app/frontend/app.py"] 