FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY data_collector/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/data/raw /app/data/predictions /app/data/raw_data \
    && chmod -R 777 /app/data

# Copy configuration
COPY configs/config.yaml /app/configs/

# Copy utilities (including the unified config parser)
COPY utilities/ /app/utilities/

# Copy source code
COPY data_collector/collector.py .
COPY data_collector/scripts/ ./scripts/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV SERVICE_NAME=data_collector

# Run the collector
CMD ["python", "collector.py"] 