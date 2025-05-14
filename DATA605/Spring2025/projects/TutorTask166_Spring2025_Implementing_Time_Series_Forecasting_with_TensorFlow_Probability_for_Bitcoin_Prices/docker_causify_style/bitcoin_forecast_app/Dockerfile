FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY bitcoin_forecast_app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/data/raw /app/data/predictions /app/data/raw_data \
    && chmod -R 777 /app/data

# Copy unified configuration
COPY configs/unified_config.yaml /app/configs/

# Copy utilities (including the unified config parser)
COPY utilities/ /app/utilities/

# Copy the src directory with models and trainers
COPY src/ /app/src/

# Copy the bitcoin forecast app
COPY bitcoin_forecast_app/models/ /app/bitcoin_forecast_app/models/
COPY bitcoin_forecast_app/mains/ /app/bitcoin_forecast_app/mains/
COPY bitcoin_forecast_app/entrypoint.sh /app/bitcoin_forecast_app/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV SERVICE_NAME=bitcoin_forecast_app

# Make entrypoint script executable
RUN chmod +x bitcoin_forecast_app/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["bash", "bitcoin_forecast_app/entrypoint.sh"] 