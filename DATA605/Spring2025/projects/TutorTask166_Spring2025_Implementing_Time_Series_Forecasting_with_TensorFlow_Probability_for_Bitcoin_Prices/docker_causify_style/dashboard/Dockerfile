FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY dashboard/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/data/raw /app/data/predictions /app/data/raw_data \
    && chmod -R 777 /app/data

# Copy unified configuration
COPY configs/unified_config.yaml /app/configs/

# Copy utilities (including the unified config parser)
COPY utilities/ /app/utilities/

# Copy the dashboard app
COPY dashboard/ /app/dashboard/

# Expose the port
EXPOSE 8501

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV SERVICE_NAME=dashboard

# Run the application
CMD ["streamlit", "run", "dashboard/app.py"] 