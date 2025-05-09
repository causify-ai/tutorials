FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY dashboard/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the src and utilities directories
COPY src /app/src
COPY utilities /app/utilities

# Create configs directory and copy config file
RUN mkdir -p /app/configs
COPY configs/config.yaml /app/configs/

# Create data directories (will be mounted as volumes)
RUN mkdir -p /app/data/predictions /app/data/raw_data

# Copy the dashboard app
COPY dashboard /app/dashboard

# Expose the port
EXPOSE 8501

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Run the application
CMD ["streamlit", "run", "dashboard/app.py"] 